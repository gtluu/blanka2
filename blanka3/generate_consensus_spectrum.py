import numpy as np
import pandas as pd
import logging
from multiprocessing import Pool
from functools import partial
from .dataset_io import *


# Calculate quality score based on signal to noise ratio.
def calculate_quality_score(scan_dict):
    peaks_df = scan_dict['peaks']
    intensity_list = peaks_df['intensity'].values.tolist()
    # Get the 2nd to 6th highest peaks in the spectrum.
    highest_peaks = sorted(intensity_list, reverse=True)[1:6]
    # quality score = mean of highest peak / median intensity
    quality_score = np.mean(highest_peaks) / np.median(sorted(intensity_list))
    scan_dict['quality_score'] = quality_score
    return scan_dict


# Calculate dot product for each scan.
def dot_product_calculation(ref_scan_dict, scan_dict):
    # Create bins for dot product calculation.
    def get_binned_peaks(ref_scan_dict, scan_dict):
        # Concatenate all scans to a single dataframe.
        concat_df = pd.concat([ref_scan_dict['peaks'], scan_dict['peaks']])
        # Use dataframe to figure out low and high m/z ranges to create bins.
        low_mz = int(round(min(concat_df['mz'].values.tolist()), -1)) - 2
        high_mz = int(round(max(concat_df['mz'].values.tolist()), -1)) - 2
        stepsize = (float(high_mz) - float(low_mz)) / 10000.0
        # NOTE: change step to precursor or fragment m/z tolerance?
        bins = np.arange(low_mz, high_mz, step=stepsize)

        # Bin peaks for each scan.
        scan_dict['binned_peaks'] = pd.cut(scan_dict['peaks']['mz'], bins=bins)
        scan_dict['binned_peaks'] = scan_dict['peaks'].groupby(scan_dict['binned_peaks']).aggregate(sum)
        ref_scan_dict['binned_peaks'] = pd.cut(ref_scan_dict['peaks']['mz'], bins=bins)
        ref_scan_dict['binned_peaks'] = ref_scan_dict['peaks'].groupby(ref_scan_dict['binned_peaks']).aggregate(sum)
        return (ref_scan_dict, scan_dict)

    # See if binned peaks exists.
    try:
        reference_binned_peaks = ref_scan_dict['binned_peaks']
        scan_binned_peaks = scan_dict['binned_peaks']
    # If no binned peaks, use regualr peaks for calculation
    except KeyError:
        ref_scan_dict, scan_dict = get_binned_peaks(ref_scan_dict, scan_dict)
        reference_binned_peaks = ref_scan_dict['binned_peaks']
        scan_binned_peaks = scan_dict['binned_peaks']

    reference_intensities = reference_binned_peaks['intensity'].values.tolist()
    scan_intensities = scan_binned_peaks['intensity'].values.tolist()

    numerator = [i * j for i, j in zip(reference_intensities, scan_intensities)]
    numerator = sum(numerator)
    denominator1 = [i**2 for i in reference_intensities]
    denominator1 = sum(denominator1)
    denominator2 = [i**2 for i in scan_intensities]
    denominator2 = sum(denominator2)
    denominator = denominator1 * denominator2
    denominator = denominator ** 0.5
    dot_product_score = numerator / denominator
    scan_dict['dot_product_score'] = dot_product_score
    return scan_dict


# Cluster replicate spectra based on dot product scores
def cluster_replicates(args, ranked_scan_dicts):
    list_of_clusters = []
    count = 0

    # Repeat clustering process until no scans with dot product score >= 0.6.
    while True:
        # Top ranked scan based on quality score.
        top_ranked_scan_dict = ranked_scan_dicts[0]
        top_ranked_scan_dict['dot_product_score'] = 1

        # Calculate dot product scores for each scan.
        dot_product_results = [dot_product_calculation(top_ranked_scan_dict, i) for i in ranked_scan_dicts[1:]]

        scans_over_threshold = [scan_dict for scan_dict in dot_product_results
                                if scan_dict['dot_product_score'] >= args['dot_product_cutoff']]
        scans_over_threshold = [top_ranked_scan_dict] + scans_over_threshold
        list_of_clusters.append((scans_over_threshold, count))

        ranked_scan_dicts = [scan_dict for scan_dict in dot_product_results
                             if scan_dict['dot_product_score'] < args['dot_product_cutoff']]
        count += 1
        if len(ranked_scan_dicts) == 0:
            break

    num_scans_largest_cluster = max([len(cluster) for cluster, count in list_of_clusters])
    list_of_largest_clusters = [cluster for cluster, count in list_of_clusters
                                if len(cluster) == num_scans_largest_cluster]

    # Return largest cluster of scans.
    return sorted(list_of_largest_clusters, key=lambda x: x[1])[0][0]


# Align spectra to generate a consensus spectrum downstream.
def align_replicates(args, cluster):

    def calculate_relative_intensity(max_intensity, intensity):
        return (intensity / max_intensity) * 100

    for scan_dict in cluster:
        scan_dict['peaks']['ion'] = scan_dict['peaks']['mz'].values.tolist()
        intensities = scan_dict['peaks']['intensity'].values.tolist()
        relative_intensities = [calculate_relative_intensity(max(intensities), i) for i in intensities]
        scan_dict['peaks']['rel_inten'] = relative_intensities

    # Each scan placed first to account for differences in peaks due to merge_asof using left outer join.
    list_of_cluster_combos = [[cluster[i]] + [j for j in cluster if not j == cluster[i]]
                              for i in range(0, len(cluster))]

    def multi_merge_asof(fragment_mz_tol, list_of_scan_dicts):
        for count, scan_dict in enumerate(list_of_scan_dicts):
            # Generate consensus spectrum in first/top quality scan.
            if count == 0:
                list_of_scan_dicts[0]['consensus'] = scan_dict['peaks']
            else:
                consensus_peaks = list_of_scan_dicts[0]['consensus']
                scan_peaks = scan_dict['peaks']
                consensus_spectrum = pd.merge_asof(consensus_peaks, scan_peaks, on='mz', tolerance=fragment_mz_tol,
                                                   direction='nearest', suffixes=['_' + str(count-1), '_' + str(count)])
                list_of_scan_dicts[0]['consensus'] = consensus_spectrum

        # Return first/top quality scan with newly generated consensus spectrum.
        return list_of_scan_dicts[0]

    # Return list of scans with consensus spectrum generated.
    return [multi_merge_asof(args['fragment_mz_tol'], cluster) for cluster in list_of_cluster_combos]


# Generate consensus spectrum from aligned replicates.
def preprocess_consensus_spectrum(scan_dict):
    consensus_spectrum = scan_dict['consensus']
    ion_columns = [i for i in consensus_spectrum.columns.values.tolist() if i.startswith('ions')]
    relative_intensity_columns = [i for i in consensus_spectrum.columns.values.tolist() if i.startswith('rel_inten')]

    consensus_spectrum['ave_mz'] = consensus_spectrum[ion_columns].mean(axis=1, skipna=True)
    consensus_spectrum['ave_rel_inten'] = consensus_spectrum[relative_intensity_columns].mean(axis=1, skipna=True)

    consensus_spectrum = consensus_spectrum[consensus_spectrum['ave_rel_inten'] != 0]
    consensus_spectrum = consensus_spectrum[['ave_mz', 'ave_rel_inten']]
    scan_dict['consensus'] = consensus_spectrum
    return scan_dict


# Generate consensus spectra based on workflow by Lam et al. (doi:10.1038/nmeth.1254).
def generate_consensus_spectrum(args, list_of_scan_dicts):
    def get_median_precursor(list_of_scan_dicts):
        return np.median([scan_dict['precursorMz'][0]['precursorMz'] for scan_dict in list_of_scan_dicts])

    def get_median_rt(list_of_scan_dicts):
        return np.median([scan_dict['retentionTime'] for scan_dict in list_of_scan_dicts])

    ranked_scan_dicts = sorted([calculate_quality_score(scan_dict) for scan_dict in list_of_scan_dicts],
                               key=lambda x: x['quality_score'], reverse=True)
    #binned_scan_dicts = get_binned_peaks(ranked_scan_dicts)
    #largest_cluster = cluster_replicates(args, binned_scan_dicts)
    largest_cluster = cluster_replicates(args, ranked_scan_dicts)
    aligned_cluster = align_replicates(args, largest_cluster)
    preprocessed_cluster = [preprocess_consensus_spectrum(i) for i in aligned_cluster]

    def multi_merge(cluster):
        for count, scan_dict in enumerate(cluster):
            peaks_df = scan_dict['consensus']
            if count == 0:
                consensus_df = peaks_df
            else:
                consensus_df = pd.merge(consensus_df, peaks_df, on='ave_mz', how='outer',
                                        suffixes=('_' + str(count-1), '_' + str(count)))

        ave_rel_inten = [i for i in consensus_df.columns.values.tolist() if i.startswith('ave_rel_inten')]
        consensus_df['intensity'] = consensus_df[ave_rel_inten].mean(axis=1, skipna=True)
        consensus_df = consensus_df[['ave_mz', 'intensity']]
        consensus_df = consensus_df.rename(columns={'ave_mz': 'mz', 'intensity': 'intensity'})
        return consensus_df

    ms_level = set([i['msLevel'] for i in list_of_scan_dicts])
    return {'peaks': multi_merge(preprocessed_cluster),
            'precursorMz': [{'precursorMz': get_median_precursor(list_of_scan_dicts)}],
            'retentionTime': get_median_rt(list_of_scan_dicts),
            'msLevel': ms_level}