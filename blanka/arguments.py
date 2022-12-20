import argparse
import os
import sys
from .timestamp import *
from multiprocessing import cpu_count


# Parse arguments to run BLANKA.
def get_args():
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Required Arguments
    parser.add_argument('--sample', help='sample input directory/file path', required=True, type=str)
    parser.add_argument('--blank', help='blank/control input directory/file path', required=True, type=str)
    parser.add_argument('--experiment', help='type of experiment (lcms or dd)', required=True, type=str)
    # Optional Arguments
    parser.add_argument('--output', help='output directory for all files generated (default=sample folder)',
                        default='', type=str)
    parser.add_argument('--blank_spot', help='name of blank condition for MALDI DD experiments', type=str)
    parser.add_argument('--snr', help='integer signal to noise ratio(default=4)', default=4, type=int)
    parser.add_argument('--rt_tol', help='retention time tolerance in seconds (default=1)', default=6.0, type=float)
    parser.add_argument('--precursor_mz_tol', help='precursor ion m/z tolerance (default=0.5)', default=0.5, type=float)
    parser.add_argument('--precursor_ppm_tol', help='precursor ion ppm tolerance (default=50)', default=50, type=float)
    parser.add_argument('--fragment_mz_tol', help='fragment ion m/z tolerance (default=0.5)', default=0.5, type=float)
    parser.add_argument('--fragment_ppm_tol', help='fragment ion ppm tolerance (default=50)', default=50, type=float)
    parser.add_argument('--dot_product_cutoff', help='dot product score cutoff for blank removal (default=0.6)',
                        default=0.6, type=float)
    # Advanced Arguments
    parser.add_argument('--cpu', help='number of threads used (default=max-1)', default=cpu_count()-1, type=int)
    parser.add_argument('--verbose', help='display progress information', default=False, type=bool)

    # Return parser
    arguments = parser.parse_args()
    return vars(arguments)


# Checks to ensure arguments are valid.
def args_check(args):
    # Check if sample and blank paths exist.
    if not os.path.exists(args['sample']):
        logging.error(get_timestamp() + ':' + 'Sample path does not exist...')
        logging.error(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    if not os.path.exists(args['blank']):
        logging.error(get_timestamp() + ':' + 'Blank path does not exist...')
        logging.error(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # Check cpu setting.
    if args['cpu'] >= cpu_count():
        logging.error(get_timestamp() + ':' + 'Number of threads specified exceeds number of available threads...')
        logging.error(get_timestamp() + ':' + 'Your computer has ' + str(cpu_count()-1) + ' usable threads...')
        logging.error(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # Check experiment.
    if not args['experiment'] == 'lcms' and not args['experiment'] == 'maldi':
        logging.error(get_timestamp() + ':' + 'Invalid experiment...')
        logging.error(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)


# Write parameters used to run BLANKA to text file.
def write_params(args, logfile):
    with open(os.path.join(os.path.split(logfile)[0], 'parameters_' + get_timestamp() + '.txt'), 'a') as params:
        for key, value in args.iteritems():
            params.write('[' + str(key) + ']' + '\n' + str(value) + '\n')


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
