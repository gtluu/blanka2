import numpy as np
import pandas as pd
import logging
from multiprocessing import Pool
from functools import partial


# Calculate quality score based on signal to noise ratio.
def calculate_quality_score(scan_dict):
    intensity_df = scan_dict['peaks'][0]['$']
    intensity_list = intensity_df['intensity'].values.tolist()
    # Get the 2nd to 6th highest peaks in the spectrum.
    highest_peaks = sorted(intensity_list, reverse=True)[1:6]
    # quality score = mean of highest peaks / median intensity
    quality_score = np.mean(highest_peaks) / np.median(sorted(intensity_list))
    scan_dict['nameValue']['quality_score'] = {'@name': 'qualityScore', '@value': quality_score}
    return scan_dict


# Create bins for dot product calculation.
def get_binned_peaks(list_of_scan_dicts):
    # Concatenate all scans to a single dataframe.
    concat_df = pd.DataFrame()
    for scan_dict in list_of_scan_dicts:
        peaks_df = scan_dict['peaks'][0]['$']
        concat_df = pd.concat([concat_df, peaks_df])

    # Use dataframe to figure out low and high m/z ranges for to create bins.
    low_mz = int(round(min(concat_df['mz'].values.tolist()))) - 2
    high_mz = int(round(max(concat_df['mz'].values.tolist()))) + 2
    bins = np.arange(low_mz, high_mz, step=0.2)

    # Bins peaks for each scan.
    for scan_dict in list_of_scan_dicts:
        peaks_df = scan_dict['peaks'][0]['$']
        binned_peaks = pd.cut(peaks_df['mz'], bins=bins)
        binned_peaks = peaks_df.groupby(binned_peaks).aggregate(sum)
        scan_dict['nameValue']['binned_peaks'] = {'@name': 'binned_peaks', '@value': binned_peaks}
    return list_of_scan_dicts


# Calculate dot product for each scan.
def dot_product_calculation(ref_scan_dict, scan_dict):
    # See if binned peaks exists.
    try:
        reference_binned_peaks = ref_scan_dict['nameValue']['binned_peaks']['@value']
        scan_binned_peaks = scan_dict['nameValue']['binned_peaks']['@value']
    # If no binned peaks, use regular peaks for calculation.
    except KeyError:
        ref_scan_dict['nameValue']['binned_peaks'] = {'@name': 'binned_peaks', '@value': ref_scan_dict['peaks'][0]['$']}
        reference_binned_peaks = ref_scan_dict['nameValue']['binned_peaks']['@value']
        scan_dict['nameValue']['binned_peaks'] = {'@name': 'binned_peaks', '@value': scan_dict['peaks'][0]['$']}
        scan_binned_peaks = scan_dict['nameValue']['binned_peaks']['@value']

    reference_intensities = reference_binned_peaks['intensity'].values.tolist()
    scan_intensities = scan_binned_peaks['intensity'].values.tolist()

    if len(reference_intensities) == len(scan_intensities):
        numerator = [i * j for i, j in zip(reference_intensities, scan_intensities)]
        numerator = sum(numerator)
        denominator1 = [i**2 for i in reference_intensities]
        denominator1 = sum(denominator1)
        denominator2 = [i**2 for i in scan_intensities]
        denominator2 = sum(denominator2)
        denominator = denominator1 * denominator2
        denominator = denominator ** 0.05
        scan_dict['nameValue']['dot_product_score'] = {'@name': 'dotProductScore', '@value': numerator / denominator}
    else:
        scan_dict['nameValue']['dot_product_score'] = {'@name': 'dotProductScore', '@value': 0}
    return scan_dict


# Cluster replicate spectra based on dot product scores.
def cluster_replicates(args, ranked_scan_dicts):
    pool = Pool(processes=args['cpu'])
    list_of_clusters = []
    count = 0

    # Repeat clustering process until no scans with dot product score >= 0.6.
    while True:
        # Top ranked scan based on quality score
        top_ranked_scan_dict = ranked_scan_dicts[0]
        top_ranked_scan_dict['nameValue']['dot_product_score']['@value'] = 1

        # Calculate dot product scores for each scan
        dot_product_results = pool.map(partial(dot_product_calculation, top_ranked_scan_dict), ranked_scan_dicts[1:])

        scans_over_threshold = [scan_dict for scan_dict in dot_product_results
                                if scan_dict['nameValue']['dot_product_score']['@value'] >= 0.6]
        scans_over_threshold = [top_ranked_scan_dict] + scans_over_threshold
        list_of_clusters.append((scans_over_threshold, count))

        ranked_scan_dicts = [scan_dict for scan_dict in dot_product_results
                             if scan_dict['nameValue']['dot_product_score']['@value'] < 0.6]
        count += 1
        if len(ranked_scan_dicts) == 0:
            break

    num_scans_largest_cluster = max([len(cluster) for cluster in list_of_clusters])
    list_of_largest_clusters = [cluster for cluster in list_of_clusters if len(cluster) == num_scans_largest_cluster]

    pool.close()
    pool.join()

    # Return largest cluster of scans.
    return sorted(list_of_largest_clusters, key=lambda x: x[1])[0][0]


# Align spectra to generate a consensus spectrum downstream.
def align_replicates(args, cluster):
    pool = Pool(processes=args['cpu'])

    def calculate_relative_intensity(max_intensity, intensity):
        return (intensity / max_intensity) * 100

    for scan_dict in cluster:
        scan_dict['peaks'][0]['$']['ion'] = scan_dict['peaks'][0]['$']['mz'].values.tolist()
        intensities = scan_dict['peaks'][0]['$']['intensity'].values.tolist()
        relative_intensities = pool.map(partial(calculate_relative_intensity, max(intensities)), intensities)
        scan_dict['peaks'][0]['$']['rel_inten'] = relative_intensities

    pool.close()
    pool.join()

    # Each scan placed first to account for differences in peaks due to merge_asof using left outer join.
    list_of_cluster_combos = [[cluster[i]] + [j for j in cluster
                                              if not j == cluster[i]]
                              for i in range(0, len(cluster))]

    def multi_merge_asof(peak_mz_tolerance, list_of_scan_dicts):
        for count, scan_dict in enumerate(list_of_scan_dicts):
            # Generate consensus spectrum in first/top quality scan.
            if count == 0:
                list_of_scan_dicts[0]['nameValue']['consensus'] = {'@name': 'consensusSpectrum',
                                                                   '@value': scan_dict['peaks'][0]['$']}
            else:
                consensus_peaks = list_of_scan_dicts[0]['nameValue']['consensus']['@value']
                scan_peaks = scan_dict['peaks'][0]['$']
                consensus_spectrum = pd.merge_asof(consensus_peaks, scan_peaks, on='mz', tolerance=peak_mz_tolerance,
                                                   direction='nearest', suffixes=['_' + str(count-1), '_' + str(count)])
                list_of_scan_dicts[0]['nameValue']['consensus'] = {'@name': 'consensusSpectrum',
                                                                   '@value': consensus_spectrum}
        # Return first/top quality scan with newly generated consensus spectrum.
        return list_of_scan_dicts[0]

    # Return list of scans with consensus spectrum generated.
    return [multi_merge_asof(args['peak_mz_tolerance'], cluster) for cluster in list_of_cluster_combos]


# Generate consensus spectrum from aligned replicates.
def preprocess_consensus_spectrum(scan_dict):
    consensus_spectrum = scan_dict['nameValue']['consensus']['@value']
    ion_columns = [i for i in consensus_spectrum.columns.values.tolist() if i.startswith('ion')]
    relative_intensity_columns = [i for i in consensus_spectrum.columns.values.tolist() if i.startswith('rel_inten')]

    consensus_spectrum['ave_mz'] = consensus_spectrum[ion_columns].mean(axis=1, skipna=True)
    consensus_spectrum['ave_rel_inten'] = consensus_spectrum[relative_intensity_columns].mean(axis=1, skipna=True)

    consensus_spectrum = consensus_spectrum[consensus_spectrum['ave_rel_inten'] != 0]
    consensus_spectrum = consensus_spectrum[['ave_mz', 'ave_rel_inten']]
    scan_dict['nameValue']['consensus']['@value'] = consensus_spectrum
    return scan_dict


# Generate consensus spectra based on workflow by Lam et al. (doi:10.1038/nmeth.1254).
def generate_consensus_spectrum(args, list_of_scan_dicts):
    pool = Pool(processes=args['cpu'])

    ranked_scan_dicts = sorted(pool.map(calculate_quality_score, list_of_scan_dicts),
                               key=lambda x: x['nameValue']['quality_score']['@value'], reverse=True)
    binned_scan_dicts = get_binned_peaks(ranked_scan_dicts)
    largest_cluster = cluster_replicates(args, binned_scan_dicts)
    aligned_cluster = align_replicates(args, largest_cluster)
    preprocessed_cluster = pool.map(preprocess_consensus_spectrum, aligned_cluster)

    pool.close()
    pool.join()

    def multi_merge(cluster):
        for count, scan_dict in enumerate(cluster):
            peaks_df = scan_dict['nameVlaue']['consensus']['@value']
            if count == 0:
                consensus_df = peaks_df
            else:
                consensus_df = pd.merge(consensus_df, peaks_df, on='ave_mz', how='outer',
                                        suffixes=('_' + str(count-1), '_' + str(count)))

        average_relative_intensity = [i for i in consensus_df.columns.values.tolist() if i.startswith('ave_rel_inten')]
        consensus_df['intensity'] = consensus_df[average_relative_intensity].mean(axis=1, skipna=True)
        consensus_df = consensus_df[['ave_mz', 'intensity']]
        consensus_df = consensus_df.rename(columns={'ave_mz': 'mz', 'intensity': 'intensity'})
        return consensus_df

    return {'peaks': [{'$': multi_merge(preprocessed_cluster)}]}


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
