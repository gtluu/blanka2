import numpy as np
import logging
from dataset_io import *


# Remove noise using mean of 5% lowest intensity peaks as noise level and user defined signal to noise ratio
def noise_removal(snr, scan_dict):
    peaks = scan_dict['peaks']
    # Filter out peaks with an intensity of 0 (absolute lowest possible baseline value).
    peaks = peaks[peaks['intensity'] != 0]
    # Calculate noise level from 5% lowest intensity peaks.
    sorted_intensities = sorted(peaks['intensity'].values.tolist())
    lowest_sorted_intensities = sorted_intensities[:int(round((len(sorted_intensities) * 0.05)))]
    if len(lowest_sorted_intensities) != 0:
        spectrum_noise = np.mean(lowest_sorted_intensities)
    else:
        # If lowest_sorted_intensities cannot be obtained, use lowest absolute intensity value in spectrum.
        spectrum_noise = min(peaks['intensity'].values.tolist())
    scan_dict['peaks'] = peaks[peaks['intensity'] >= (snr * spectrum_noise)]
    return scan_dict


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
