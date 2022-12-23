import subprocess
import pandas as pd
from functools import partial
from psims.transform import MzMLTransformer
from blanka import *


def run_blanka(args, falcon_keys):
    # Args check.
    args_check(args)
    args['version'] = '2.0.0'

    # Initialize logger if not running on server.
    logname = 'log_' + get_timestamp() + '.log'
    if args['outdir'] == '':
        if os.path.isdir(args['sample_input']):
            logfile = os.path.join(args['sample_input'], logname)
        else:
            logfile = os.path.split(args['sample_input'])[0]
            logfile = os.path.join(logfile, logname)
    else:
        logfile = os.path.join(args['outdir'], logname)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=logfile, level=logging.INFO)
    if args['verbose']:
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # Check to make sure using Python 3.8.
    if not sys.version_info.major == 3 and sys.version_info_major == 8:
        logging.warning(get_timestamp() + 'Must be using Python 3.8 to run BLANKA2.')
        sys.exit(1)

    # Check to make sure running on macOS or Linux.
    if not sys.platform == 'linux' and not sys.platform == 'darwin':
        logging.warning(get_timestamp() + 'Must be using macOS or Linux.')
        logging.warning(get_timestamp() + 'If using Windows, please use Windows Subsystem for Linux (WSL).')

    # Log arguments.
    for key, value in args.items():
        logging.info(get_timestamp() + ':' + str(key) + ':' + str(value))

    # Get filenames for input data.
    if not args['sample_input'].lower().endswith('.mzml'):
        sample_files = mzml_data_detection(args['sample_input'])
    elif args['sample_input'].lower().endswith('.mzml'):
        sample_files = [args['sample_input']]
    if not args['blank_input'].lower().endswith('.mzml'):
        blank_files = mzml_data_detection(args['blank_input'])
    elif args['blank_input'].lower().endswith('.mzml'):
        blank_files = [args['blank_input']]

    # Run falcon cluster.
    logging.info(get_timestamp() + ':' + 'Running falcon cluster...')
    falcon_cmd = ['falcon'] + sample_files + blank_files
    falcon_results_filename = 'falcon_' + get_timestamp()
    falcon_results_filename = os.path.join(args['outdir'], falcon_results_filename)
    falcon_cmd.append(falcon_results_filename)
    for key in falcon_keys:
        if args[key] == True:
            falcon_cmd.append('--' + key)
        else:
            if args[key] != False:
                if args[key] != '':
                    falcon_cmd.append('--' + key)
                    falcon_cmd.append(str(args[key]))
    subprocess.run(falcon_cmd, shell=True, capture_output=True)

    # Read in and parse falcon cluster results to figure which scans to exclude from each sample based on clustering
    # with blanks.
    # Get initial dataframe with falcon results and reformat with new columns from "identifier".
    logging.info(get_timestamp() + ':' + 'Parsing scans to be removed from sample .mzML files...')
    falcon_results = pd.read_csv(falcon_results_filename, comment='#')
    falcon_results[['mzspec_const',
                    'usi',
                    'sample',
                    'scan_const',
                    'scan']] = falcon_results['identifier'].str.split(':', expand=True)
    falcon_results = falcon_results.drop(labels=['identifier', 'mzspec_const', 'usi', 'scan_const'], axis=1)
    # Remove singletons from dataframe.
    falcon_results = falcon_results[falcon_results['cluster'] != -1]
    falcon_results = falcon_results.sort_values(by='cluster', ignore_index=True)
    # Get scans to be removed for each sample.
    blank_ids = [os.path.splitext(os.path.split(blank)[-1])[0] for blank in blank_files]
    sample_scan_removal_lists = {os.path.splitext(os.path.split(sample)[-1])[0]: [] for sample in sample_files}
    for cluster_id in range(0, max(falcon_results['cluster'] + 1)):
        # Only care about clusters with blanks.
        cluster = falcon_results[falcon_results['cluster'] == cluster_id]
        if True in cluster['sample'].isin(blank_ids).values.tolist():
            # Remove rows with blank scan info from cluster and add to sample scan list for check later.
            cluster = cluster[~cluster['sample'].isin(blank_ids)]
            if not cluster.empty:
                for sample_id, scan_removal_list in sample_scan_removal_lists.items():
                    tmp_df = cluster[cluster['sample'] == sample_id]
                    sample_scan_removal_lists[sample_id] += tmp_df['scan'].values.tolist()

    # Add 'scan=' prefix to scan removal lists.
    for sample_id, scan_removal_list in sample_scan_removal_lists.items():
        sample_scan_removal_lists[sample_id] = ['scan=' + i for i in scan_removal_list]

    # Transformation function for MzMLTransformer.
    def transform_drop_scans(spectrum, scans_to_remove):
        if spectrum['id'] in scans_to_remove:
            return None
        return spectrum

    # Load in each sample file and rewrite without scans that clustered with scans from blanks.
    for infile in sample_files:
        # Transform files with psims transformer.
        # TODO: psims transformer does not transcribe ion mobility arrays; will need to fork it for that functionality
        logging.info(get_timestamp() + ':' + 'Removing scans from ' + os.path.split(infile)[1] + ' found in blanks...')
        if args['outfile'] == '':
            args['outfile'] = os.path.splitext(os.path.split(infile)[-1])[0] + '_blanka.mzML'

        infile_id = os.path.splitext(os.path.split(infile)[-1])[0]
        transform_partial = partial(transform_drop_scans, scans_to_remove=sample_scan_removal_lists[infile_id])
        with open(infile, 'rb') as instream, open(os.path.join(args['outdir'], args['outfile']), 'wb') as outstream:
            MzMLTransformer(instream, outstream, transform_partial).write()
        logging.info(get_timestamp() + ':' + 'Finished writing to ' + args['outfile'])

    # Shut down logger.
    for hand in logging.getLogger().handlers:
        logging.getLogger().removeHandler(hand)
    logging.shutdown()


if __name__ == '__main__':
    # parse arguments
    args, falcon_keys = get_args()

    # Run
    run_blanka(args, falcon_keys)
