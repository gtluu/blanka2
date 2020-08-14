from .generate_consensus_spectrum import *


# Select control spectrum to use for blank removal for LC-MS data based on MS mode, retention time, and precursor m/z.
def select_control_spectrum_lcms(args, control_spectra, sample_spectrum):
    ms_level = int(sample_spectrum['@msLevel'])
    sample_rt = float(sample_spectrum['@retentionTime'][2:-1])
    rt_tol = args['retention_time_tolerance']
    sample_pre_mz = float(sample_spectrum['precursorMz'][0]['$'])
    pre_mz_tol = args['precursor_mz_tolerance']

    # Search by retention time for MS1 spectra.
    if ms_level == 1:
        control_spectra_list = []
        for spectrum in control_spectra:
            control_rt = float(spectrum['@retentionTime'][2:-1])
            if ms_level == 1:
                if (control_rt + rt_tol) >= sample_rt >= (control_rt - rt_tol):
                    control_spectra_list.append(spectrum)
    # Search by retention time and precursor m/z for MS2 spectra.
    elif ms_level >= 2:
        control_spectra_list = []
        for spectrum in control_spectra:
            control_rt = float(spectrum['@retentionTime'][2:-1])
            control_pre_mz = float(spectrum['precursorMz'][0]['$'])
            if (control_rt + rt_tol) >= sample_rt >= (control_rt - rt_tol) and \
                    (control_pre_mz + pre_mz_tol) >= sample_pre_mz >= (control_pre_mz - pre_mz_tol):
                control_spectra_list.append(spectrum)

    # Return None if no matching spectra found.
    # Continue if matching spectra found.
    if len(control_spectra_list) != 0:
        # Return best match if more than one spectra found meeting criteria.
        # Return spectrum most similar to sample based on dot product score.
        if len(control_spectra_list) > 1:
            return sorted([dot_product_calculation(sample_spectrum, i) for i in control_spectra_list],
                          key=lambda x: x['nameValue']['dot_product_score']['@value'], reverse=True)
        # Return control spectrum if only one found.
        elif len(control_spectra_list) == 1:
            return control_spectra_list[0]


# Remove control spectrum peaks from sample spectrum if m/z within specified tolerance for MS1 spectra
# Remove sample spectrum if corresponding spectrum is found in control dataset for MS^n spectra.
# Return sample spectrum if sample spectrum is empty.
# Return None if matched peaks intensities <= MS1/MS2 thresholds for respective spectra.
def blank_removal(args, control_spectrum, sample_spectrum):
    try:
        sample_spectrum_df = sample_spectrum['peaks'][0]['$']
        control_spectrum_df = control_spectrum['peaks'][0]['$']
        ms_level = int(sample_spectrum['@msLevel'])

        if sample_spectrum_df.empty:
            return sample_spectrum

        blank_subtracted_df = pd.merge_asof(sample_spectrum_df.sort_values('mz'), control_spectrum_df.sort_values('mz'),
                                            on='mz', tolerance=args['peak_mz_tolerance'], direction='nearest').fillna(0)
        blank_subtracted_df = blank_subtracted_df[blank_subtracted_df['intensity_y'] == 0]

        if ms_level == 1:
            threshold = args['ms1_threshold']
        elif ms_level >= 2:
            threshold = args['ms2_threshold']

        blankless_total_ion_count = sum(blank_subtracted_df['intensity_x'].values.tolist())
        sample_total_ion_count = sum(sample_spectrum_df['intensity'].values.tolist())

        if (blankless_total_ion_count / sample_total_ion_count) <= threshold:
            blank_subtracted_df = blank_subtracted_df[['mz', 'intesnity_x']]
            blank_subtracted_df = blank_subtracted_df.rename(columns={'mz': 'mz', 'intensity_x': 'intensity'})
            sample_spectrum['peaks'][0]['$'] = blank_subtracted_df
            return sample_spectrum
    except KeyError:
        return sample_spectrum


# Select control spectrum and remove blanks
def spectra_compare(args, control_spectra, sample_spectrum):
    control_spectrum = select_control_spectrum_lcms(args, control_spectra, sample_spectrum)
    if control_spectrum is None:
        return sample_spectrum
    else:
        return blank_removal(args, control_spectrum, sample_spectrum)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
