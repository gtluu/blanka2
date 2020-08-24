import os
import sys
import platform
import subprocess
from mzxml_io import *
from timestamp import *
import generate_consensus_spectrum


# Scan directory for mzXML files.
def mzxml_data_detection(directory):
    return [os.path.join(dirpath, filename) for dirpath, dirnames, filenames in os.walk(directory)
            for filename in filenames if os.path.splitext(filename)[1].lower() == '.mzxml']


# Get list of sample filepaths from input arguments.
def get_sample_list(args):
    if os.path.splitext(args['sample'])[1].lower() == '.mzxml':
        sample_file_list = [args['sample']]
    elif os.path.splitext(args['sample'])[1].lower() == '':
        sample_file_list = mzxml_data_detection(args['sample'])
        if sample_file_list == []:
            logging.error(get_timestamp() + ':' + 'No sample .mzXML files found...')
            logging.error(get_timestamp() + ':' + 'Exiting...')
            sys.exit(1)
    # Returns list of .mzXML filepaths.
    return sample_file_list


# Group spectra from replicate .mzXML files based on precursor m/z and retention time
def group_replicate_spectra(args, list_of_scan_dicts):
    # new_scan_dicts is a list of list of scan_dicts, where each list of dicts is a list of presumably replicate spectra
    new_scan_dicts = []
    for scan_dict in list_of_scan_dicts:
        if scan_dict['msLevel'] == 1:
            retention_time = scan_dict['retentionTime']
            tmp_list = []
            for scan_dict2 in list_of_scan_dicts:
                if scan_dict2['msLevel'] == 1:
                    if abs(scan_dict2['retentionTime'] - retention_time) <= args['rt_tol']:
                        tmp_list.append(scan_dict2)
            new_scan_dicts.append(tmp_list)
        elif scan_dict['msLevel'] >= 2:
            precursor_mz = scan_dict['precursorMz'][0]['precursorMz']
            retention_time = scan_dict['retentionTime']
            tmp_list = []
            for scan_dict2 in list_of_scan_dicts:
                if scan_dict2['msLevel'] >= 2:
                    if abs(scan_dict2['precursorMz'][0]['precursorMz'] - precursor_mz) <= args['precursor_mz_tol'] and\
                      abs(scan_dict2['retentionTime'] - retention_time) <= args['rt_tol']:
                        tmp_list.append(scan_dict2)
            new_scan_dicts.append(tmp_list)
    return new_scan_dicts


# Load in sample data.
def load_sample_data(sample_file):
    sample_data = read_mzxml(sample_file)
    tmp_list = []
    for scan_dict in sample_data:
        scan_dict['file'] = sample_file
        tmp_list.append(scan_dict)
    sample_data = tmp_list
    return sample_data


# Load in blank data.
# Currently does not take into account multiple replicates, real vs not spectra, etc.
def load_blank_data(args):
    if os.path.splitext(args['blank'])[1].lower() == '.mzxml':
        # Read in mzXML scans as a list of dicts.
        blank_data = []
        list_of_scan_dicts = read_mzxml(args['blank'])
        for scan_dict in list_of_scan_dicts:
            scan_dict['file'] = args['blank']
            blank_data.append(scan_dict)
        return blank_data
    elif os.path.splitext(args['blank'])[1].lower() == '':
        blank_file_list = mzxml_data_detection(args['blank'])
        if blank_file_list == []:
            logging.error(get_timestamp() + ':' + 'No blank .mzXML files found...')
            logging.error(get_timestamp() + ':' + 'Exiting...')
            sys.exit(1)
        else:
            # Read in blank .mzXML file.
            blank_data = []
            for blank in blank_file_list:
                list_of_scan_dicts = read_mzxml(blank)
                for scan_dict in list_of_scan_dicts:
                    scan_dict['file'] = blank
                    blank_data.append(scan_dict)
            '''grouped_blank_data = group_replicate_spectra(args, blank_data)
            consensus_blank_data = []
            # group == list_of_scan_dicts
            for group in grouped_blank_data:
                ms_level = set([i['msLevel'] for i in group])
                if len(ms_level) == 1:
                    ms_level = list(ms_level)[0]
                if int(ms_level) == 1:
                    # generate_consensus_peak_list
                    pass
                elif int(ms_level) >= 2:
                    tmp = generate_consensus_spectrum.get_consensus_spectrum(args, group)
                    consensus_blank_data.append(tmp)
            return consensus_blank_data'''
            return blank_data


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
