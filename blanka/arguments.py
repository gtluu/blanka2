import argparse
import os
import sys
from blanka.timestamp import *


# TODO: add descriptions for falcon cluster params
def arg_descriptions():
    descriptions = {'sample_input': 'Filepath for sample .mzML file or directory containing multiple .mzML files.',
                    'blank_input': 'Filepath for blank/control .mzML file or directory containing multiple .mzML files.'
                                   ' MS/MS spectra from samples will be removed if clustered to spectra in blank '
                                   'file(s).',
                    'outdir': 'Path to folder in which to write output file(s). Default = none',
                    'outfile': 'User defined filename for output if converting a single file, otherwise files will '
                               'have same filename and overwrite each other. Default = none.',
                    'verbose': 'Boolean flag to determine whether to print logging output.'}
    return descriptions


# Parse arguments to run BLANKA.
def get_args():
    desc = arg_descriptions()

    # Initialize parser
    parser = argparse.ArgumentParser()

    # Required Arguments
    required = parser.add_argument_group('Required Parameters')
    required.add_argument('--sample_input', help=desc['sample_input'], required=True, type=str)
    required.add_argument('--blank_input', help=desc['blank_input'], required=True, type=str)

    # Optional Arguments
    optional = parser.add_argument_group('Optional Parameters')
    optional.add_argument('--outdir', help=desc['outdir'], default='', type=str)
    optional.add_argument('--outfile', help=desc['outfile'], default='', type=str)
    optional.add_argument('--verbose', help=desc['verbose'], action='store_true')

    # Return parser
    arguments = parser.parse_args()
    return vars(arguments)


# Checks to ensure arguments are valid.
def args_check(args):
    # Check if input file/directory exists.
    if not os.path.exists(args['sample_input']):
        logging.info(get_timestamp() + ':' + 'Sample input path does not exist...')
        logging.info(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    if not os.path.exists(args['blank_input']):
        logging.info(get_timestamp() + ':' + 'Blank input path does not exist...')
        logging.info(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # Check if output directory exists and create it if it does not.
    if not os.path.isdir(args['outdir']) and args['outdir'] != '':
        os.makedirs(args['outdir'])
    # Check to make sure output filename ends in .mzML extension.
    if os.path.splitext(args['outfile']) != '.mzML' and args['outfile'] != '':
        args['outfile'] = args['outfile'] + '.mzML'


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
