from blanka3 import *


def run_blanka(args):
    logging.info(get_timestamp() + ':' + 'Running BLANKA...')

    # Make user-specified output directory if it doesn't exist yet.
    if not os.path.isdir(args['output']) and args['output'] != '':
        logging.info(get_timestamp() + ':' + 'Creating Output Directory')
        os.mkdir(args['output'])

    # Load in sample data.
    logging.info(get_timestamp() + ':' + 'Loading all sample data...')
    sample_file_list = get_sample_list(args)

    # Load in blank data.
    logging.info(get_timestamp() + ':' + 'Loading all blank data...')
    blank_data = filter(None, load_blank_data(args))

    # Remove noise from blank data.
    # blank_noiseless_data == list of scans from all control datasets
    logging.info(get_timestamp() + ':' + 'Removing noise from control data...')
    # APPLY A PEAK PICKING ALGORITHM HERE?
    blank_ms2 = [i for i in blank_data if i['msLevel'] >= 2]
    blank_ms2 = sorted(blank_ms2, key=lambda x: x['precursorMz'][0]['precursorMz'])

    # Process each sample file individually
    for sample in sample_file_list:
        if args['blank'] != sample:
            # Initialize BLANKA output file name.
            if args['output'] == '':
                # ex: C:\folder\filename
                blanka_output = os.path.splitext(sample)[0] + '_blanka.mzXML'
            else:
                blanka_output = os.path.split(sample)[1]
                blanka_output = os.path.splitext(blanka_output)[0]
                blanka_output = os.path.join(args['output'], blanka_output + '_blanka.mzXML')

            # Read in sample data.
            logging.info(get_timestamp() + ':' + 'Processing ' + os.path.split(sample)[1] + '...')
            sample_data = filter(None, load_sample_data(sample))

            # Blank spectra removal.
            spectra_for_removal = [compare_sample_blank(args, blank_ms2, i)
                                   for i in sample_data]
            spectra_for_removal = filter(None, spectra_for_removal)

            # Remove selected spectra/scans from .mzXML file and modify metadata accordingly.
            logging.info(get_timestamp() + ':' + 'Writing data to ' + blanka_output + '...')
            modify_mzxml(blanka_output, spectra_for_removal, sample)


if __name__ == '__main__':
    # Start timer for prcoessing time.
    start = timeit.default_timer()

    # Parse arguments.
    arguments = get_args()

    # Initialize logger.
    if arguments['output'] == '':
        if os.path.isdir(arguments['sample']):
            logfile = os.path.join(arguments['sample'], 'blanka_log_' + get_timestamp() + '.log')
        else:
            logfile = os.path.split(arguments['sample'])[0]
            logfile = os.path.join(logfile, 'blanka_log_' + get_timestamp() + '.log')
    else:
        logfile = os.path.join(arguments['output'], 'blanka_log_' + get_timestamp() + '.log')
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=logfile, level=logging.INFO)
    if arguments['verbose']:
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logger = logging.getLogger(__name__)

    # Check arguments.
    args_check(arguments)
    arguments['version'] = '1'

    # Write out parameters used.
    write_params(arguments, logfile)

    # Initialize multiprocessing pool.
    pool = Pool(processes=arguments['cpu'])

    # Run BLANKA
    run_blanka(arguments)

    # Close multiprocessing pool.
    pool.close()
    pool.join()

    # Log runtime.
    logging.info(get_timestamp() + ':' + 'Total Runtime: ' + str(timeit.default_timer() - start) + ' sec')
