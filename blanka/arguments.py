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

    falcon_desc = {'work_dir': 'Working directory for falcon cluster (default: temporary directory).',
                   'overwrite': 'Overwrite existing results (default: do not overwrite).',
                   'export_representatives': 'Export cluster representatives to an MGF file (default: no export).',
                   'export_include_singletons': 'Include singletons in the cluster representatives MGF file '
                                                '(default: do not include singletons).',
                   'usi_pxd': 'ProteomeXchange dataset identifier to create Universal Spectrum Identifier references '
                              '(default: USI000000).',
                   'precursor_tol': 'Precursor tolerance mass and mode (default: 20 ppm). Mode should be either '
                                    '"ppm" or "Da".',
                   'rt_tol': 'Retention time tolerance (default: no retention time filtering).',
                   'fragment_tol': 'Fragment mass tolerance in m/z (default: 0.05 m/z).',
                   'eps': 'The eps parameter (cosine distance) for DBSCAN clustering (default: 0.1). Relevant cosine '
                          'distance thresholds are typically between 0.05 and 0.30.',
                   'min_samples': 'The min_samples parameter for DBSCAN clustering (default: 2).',
                   'mz_interval': 'Precursor m/z interval (centered around x.5 Da) to process spectra simultaneously '
                                  '(default: 1 m/z).',
                   'hash_len': 'Hashed vector length (default: 800).',
                   'n_neighbors': 'Number of neighbors to include int he pairwise distance matrix for each spectrum '
                                  '(default: 64).',
                   'n_neighbors_ann': 'Number of neighbors to retrieve from the nearest neighbor indexes prior to '
                                      'precursor toelrance filterint (default: 128).',
                   'batch_size': 'Number of spectra to process simultaneously (default: 65536).',
                   'n_probe': 'Maximum number of lists in the inverted index to inspect during querying (default: '
                              '32).',
                   'min_peaks': 'Discard spectra with fewer than this number of peaks (default: 5).',
                   'min_mz_range': 'Discard spectra with a smaller mass range (default: 250.0 m/z).',
                   'min_mz': 'Minimum peak m/z value (inclusive, default: 101.0 m/z).',
                   'max_mz': 'Maximum peak m/z value (inclusive, default: 1500.0 m/z).',
                   'remove precursor_tol': 'Window around the precursor mass to remove peaks (default: 1.5 m/z).',
                   'min_intensity': 'Remove pekas with a lower intensity relative to the base intensity (default: '
                                    '0.01).',
                   'max_peaks_used': 'Only use the specified most intense peaks in the spectra (default: 50).',
                   'scaling': 'Peak scaling method used to reduce the influence of very intense peaks (default: off).'}
    return descriptions, falcon_desc


# Parse arguments to run BLANKA.
def get_args():
    desc, falcon_desc = arg_descriptions()

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

    # Falcon Arguments
    falcon = parser.add_argument_group('Falcon Parameters')
    falcon.add_argument('--work_dir', help=falcon_desc['work_dir'], default='', type=str)
    falcon.add_argument('--overwrite', help=falcon_desc['overwrite'], action='store_true')
    falcon.add_argument('--export_representatives', help=falcon_desc['export_representatives'], action='store_true')
    falcon.add_argument('--export_include_singletons', help=falcon_desc['export_include_singletons'],
                        action='store_true')
    falcon.add_argument('--usi_pxd', help=falcon_desc['usi_pxd'], default='USI000000', type=str)
    falcon.add_argument('--precursor_tol', help=falcon_desc['precursor_tol'], nargs=2, default=[20, 'ppm'])
    falcon.add_argument('--rt_tol', help=falcon_desc['rt_tol'], default=None, type=float)
    falcon.add_argument('--fragment_tol', help=falcon_desc['fragment_tol'], default=0.05, type=float)
    falcon.add_argument('--eps', help=falcon_desc['eps'], default=0.1, type=float)
    falcon.add_argument('--min_samples', help=falcon_desc['min_samples'], default=2, type=int)
    falcon.add_argument('--mz_interval', help=falcon_desc['mz_interval'], default=1, type=int)
    falcon.add_argument('--hash_len', help=falcon_desc['hash_len'], default=800, type=int)
    falcon.add_argument('--n_neighbors', help=falcon_desc['n_neighbors'], default=64, type=int)
    falcon.add_argument('--n_neighbors_ann', help=falcon_desc['n_neighbors_ann'], default=128, type=int)
    falcon.add_argument('--batch_size', help=falcon_desc['batch_size'], default=65536, type=int)
    falcon.add_argument('--n_probe', help=falcon_desc['n_probe'], default=32, type=int)
    falcon.add_argument('--min_peaks', help=falcon_desc['min_peaks'], default=5, type=int)
    falcon.add_argument('--min_mz_range', help=falcon_desc['min_mz_range'], default=250.0, type=float)
    falcon.add_argument('--min_mz', help=falcon_desc['min_mz'], default=101.0, type=float)
    falcon.add_argument('--max_mz', help=falcon_desc['max_mz'], default=1500.0, type=float)
    falcon.add_argument('--remove_precursor_tol', help=falcon_desc['remove_precursor_tol'], default=1.5, type=float)
    falcon.add_argument('--min_intensity', help=falcon_desc['min_intensity'], default=0.01, type=float)
    falcon.add_argument('--max_peaks_used', help=falcon_desc['max_peaks_used'], default=50, type=int)
    falcon.add_argument('--scaling', help=falcon_desc['scaling'], default='off', type=str,
                        choices=['off', 'root', 'log', 'rank'])

    # Return parser
    arguments = parser.parse_args()
    return vars(arguments), falcon_desc.keys()


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
