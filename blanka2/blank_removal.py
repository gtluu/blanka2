from generate_consensus_spectrum import *
from timestamp import *


# Check sample spectrum against blank spectra using dot product score.
def compare_sample_blank(args, blank_spectra, sample_spectrum):
    logging.info(get_timestamp() + ':' + 'Checking Scan ' + str(sample_spectrum['num']) + '...')
    ms_level = int(sample_spectrum['msLevel'])
    sample_rt = float(sample_spectrum['retentionTime'])
    rt_tol = args['rt_tol']
    if ms_level >= 2:
        sample_pre_mz = float(sample_spectrum['precursorMz'][0]['precursorMz'])
    pre_mz_tol = args['precursor_mz_tol']

    # Search for matching blank spectrum by retention time and precursor m/z for MS2 spectra.
    # MS1 spectra not searched
    if ms_level >= 2:
        blank_spectra_list = []
        for spectrum in blank_spectra:
            if int(spectrum['msLevel']) >= 2:
                blank_rt = float(spectrum['retentionTime'])
                blank_pre_mz = float(spectrum['precursorMz'][0]['precursorMz'])
                if abs(blank_rt - sample_rt) <= rt_tol and abs(blank_pre_mz - sample_pre_mz) <= pre_mz_tol:
                    blank_spectra_list.append(spectrum)
    else:
        return None

    # Return None if no matching spectra found.
    # Continue if matching spectra found.
    if len(blank_spectra_list) != 0:
        # Return best match if more than one spectra found meeting criteria.
        # Return spectrum most similar to sample based on dot product score.
        if len(blank_spectra_list) > 1:
            blank_spectrum = sorted([dot_product_calculation(args, sample_spectrum, i) for i in blank_spectra_list],
                                    key=lambda x: x['dot_product_score'], reverse=True)[0]
        # Return blank spectrum if only one found.
        elif len(blank_spectra_list) == 1:
            blank_spectrum = dot_product_calculation(args, sample_spectrum, blank_spectra_list[0])
        if blank_spectrum['dot_product_score'] >= args['dot_product_cutoff']:
            return sample_spectrum


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
