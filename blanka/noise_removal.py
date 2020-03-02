import logging


# Remove noise using mean of 5% lowest intensity peaks as noise level and user defined signal to noise ratio.
def noise_removal(snr, scan_dict):
    try:
        peaks = scan_dict['peaks'][0]['$']
        peaks = peaks[peaks['intensity'] != 0]
        sorted_intensities = sorted(peaks['intensity'].values.tolist())
        lowest_sorted_intensities = sorted_intensities[:int(round((len(sorted_intensities) * 0.05)))]
        if len(lowest_sorted_intensities) != 0:
            spectrum_noise = sum(lowest_sorted_intensities) / len(lowest_sorted_intensities)
        else:
            spectrum_noise = min(peaks['intensity'].values.tolist())
        scan_dict['peaks'][0]['$'] = peaks[peaks['intensity'] >= (snr * spectrum_noise)]
    except KeyError:
        pass
    return scan_dict


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
