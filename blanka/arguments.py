import argparse
import os
import sys
from timestamp import *
from multiprocessing import cpu_count


# Parse arguments to run BLANKA.
def get_args():
    parser = argparse.ArgumentParser()
    # Required Arguments
    parser.add_argument('--sample', help="sample input directory/file", required=True, type=str)
    parser.add_argument('--control', help="control input file path with '.mzXML' file extension (lcq/qtof) or \
                                           name of control sample spot (dd)", required=True, type=str)
    parser.add_argument('--instrument', help="instrument/experiment (choose 'lcq', 'qtof', 'dd'", required=True,
                        type=str)
    # Optional Arguments
    parser.add_argument('--output', help="output directory for all generated files; default=source folder",
                        default='', type=str)
    parser.add_argument('--signal_noise_ratio', help="integer signal to noise ratio (default=4)", default=4,
                        type=int)
    parser.add_argument('--retention_time_tolerance', help="retention time error in seconds (default=0.1s)",
                        default=0.1, type=float)
    parser.add_argument('--precursor_mz_tolerance', help="absolute precursor m/z error in Da (default=0.02 Da",
                        default=0.02, type=float)
    parser.add_argument('--peak_mz_tolerance', help="absolute peak m/z error in Da (default=0.02 Da",
                        default=0.02, type=float)
    parser.add_argument('--noise_removal_only', help="only perform noise removal (no blank removal)", default=False,
                        type=bool)
    parser.add_argument('--blank_removal_only', help="only perform blank removal (no noise removal)", default=False,
                        type=bool)
    parser.add_argument('--ms1_threshold', help="intensity threshold for MS1 spectra removal", default=0.5, type=float)
    parser.add_argument('--ms2_threshold', help="intensity threshold for MS2 spectra removal", default=0.2, type=float)
    parser.add_argument('--cpu', help="number of threads used (default=max-1)", default=cpu_count()-1, type=int)
    parser.add_argument('--verbose', help="display progress information", default=False, type=bool)
    arguments = parser.parse_args()
    return vars(arguments)


# Checks to ensure arguments are valid.
def args_check(args):
    # check sample and control path
    if not os.path.exists(args['sample']):
        logging.error(get_timestamp() + ':' + 'Sample path does not exist...')
        logging.error(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    if not os.path.exists(args['control']):
        logging.error(get_timestamp() + ':' + 'Control path does not exist...')
        logging.error(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # check blank removal thresholds
    if args['ms1_threshold'] > 1:
        logging.error(get_timestamp() + ':' + 'MS1 Threshold must be <= 1...')
        logging.error(get_timestamp() + ':' + 'Exiting...')
    if args['ms2_threshold'] > 1:
        logging.error(get_timestamp() + ':' + 'MS2 Threshold must be <= 1...')
        logging.error(get_timestamp() + ':' + 'Exiting...')
    # check --cpu
    if args['cpu'] >= cpu_count():
        logging.error(get_timestamp() + ':' + 'Number of threads specified exceeds number of available threads...')
        logging.error(get_timestamp() + ':' + 'Your computer has ' + str(cpu_count() - 1) + ' usable threads...')
        logging.error(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # check --instrument
    if not args['instrument'] == 'lcq' and not args['instrument'] == 'qtof' and not args['instrument'] == 'dd':
        logging.error(get_timestamp() + ':' + 'Invalid instrument...')
        logging.error(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # check noise and blank removal only options
    if args['noise_removal_only'] and args['blank_removal_only']:
        logging.error(get_timestamp() + ':' +
                      '--noise_removal_only and --blank_removal_only both cannot be selected at once...')
        logging.error(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)


# Write parameters used to run BLANKA to text file.
def write_params(args, logfile):
    with open(os.path.join(os.path.split(logfile)[0], 'parameters_' + get_timestamp() + '.txt'), 'a') as params:
        for key, value in args.iteritems():
            params.write('[' + str(key) + ']' + '\n' + str(value) + '\n')


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
