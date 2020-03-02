from blanka import *


def run_blanka(args):
    logging.info(get_timestamp() + ':' + 'Running BLANKA...')
    filetypes = ['.t2d', '.d', '.yep', '.baf', 'fid', '.tdf', '.wiff', '.wiff2', '.lcd', '.raw', '.unifi']

    # Make user-specified output directory if it doesn't exist yet.
    if not os.path.isdir(args['output']) and args['output'] != '':
        logging.info(get_timestamp() + ':' + 'Creating Output Directory...')
        os.mkdir(args['output'])

    # Load in sample data and convert to mzXML if necessary.
    logging.info(get_timestamp() + ':' + 'Loading all sample data...')
    sample_file_list = load_sample_data(args, filetypes)

    # Load in control data and convert to mzXML if necessary.
    logging.info(get_timestamp() + ':' + 'Loading all control data...')
    control_data = load_control_data(args, filetypes)

    # Remove noise from control data.
    # control_noiseless_data == list of scans from all control datasets
    logging.info(get_timestamp() + ':' + 'Removing noise from control data...')
    control_noiseless_data = [pool.map(partial(noise_removal, args['signal_noise_ratio']), i) for i in control_data]

    # Process each sample file individually.
    for dataset in sample_file_list:
        if args['control'] != dataset and not dataset.startswith(args['control']):

            # Initialize BLANKA output file name.
            if args['output'] == '':
                # ex: C:\folder\filename
                blanka_output = os.path.splitext(dataset)[0] + '_blanka'
            else:
                blanka_output = os.path.split(dataset)[1]
                blanka_output = os.path.splitext(blanka_output)[0]
                blanka_output = os.path.join(args['output'], blanka_output + '_blanka')

            # Read in sample data.
            logging.info(get_timestamp() + ':' + 'Processing ' + os.path.split(dataset)[1] + '...')
            sample_data = read_mzxml(dataset)

            # Noise removal when running full processing or only performing noise removal.
            if (args['noise_removal_only'] == False and args['blank_removal_only'] == False) or \
                    args['noise_removal_only'] == True:

                logging.info(get_timestamp() + ':' + 'Removing noise from ' + os.path.split(dataset)[1] + '...')
                sample_data['msRun']['scan'] = pool.map(partial(noise_removal, args['signal_noise_ratio']),
                                                        sample_data['msRun']['scan'])

                # Add dataProcessing element to mzXML output file for noise removal w/ BLANKA.
                blanka_output += '_noise_removed'
                sample_data['msRun']['dataProcessing'].append({'@centroided': True,
                                                               'software': {'@name': 'BLANKA',
                                                                            '@type': 'noise removal',
                                                                            '@version': args['version']},
                                                               'processingOperation': {'@name': 'noise removal'}})

            # Blank removal when running full processing or only performing blank removal.
            if (args['noise_removal_only'] == False and args['blank_removal_only'] == False) or \
                    args['blank_removal_only'] == True:

                logging.info(get_timestamp() + ':' + 'Removing blank spectra from ' + os.path.split(dataset)[1] + '...')
                # control_spectra == list of scan dicts for lcms, control_spectra == concensus spectrum for dd
                for control_dataset in control_noiseless_data:
                    # Process LC-MS data.
                    if args['instrument'] != 'dd':
                        sample_data_scan_args = partial(spectra_compare, args, control_dataset)
                        sample_data['msRun']['scan'] = pool.map(sample_data_scan_args, sample_data['msRun']['scan'])
                        sample_data['msRun']['scan'] = filter(None, sample_data['msRun']['scan'])
                    # Process MALDI-TOF DD data.
                    else:
                        for control_spectrum in control_dataset:
                            sample_data_scan_args = partial(blank_removal, args['peak_mz_tolerance'], control_spectrum)
                            sample_data['msRun']['scan'] = pool.map(sample_data_scan_args, sample_data['msRun']['scan'])
                            sample_data['msRun']['scan'] = filter(None, sample_data['msRun']['scan'])

                # Add dataProcessing element to mzXML output file for blank removal w/ BLANKA.
                blanka_output += '_blank_removed'
                sample_data['msRun']['dataProcessing'].append({'@centroided': True,
                                                               'software': {'@name': 'BLANKA',
                                                                            '@type': 'blank removal',
                                                                            '@version': args['version']},
                                                               'processingOperation': {'@name': 'blank removal'}})
            # write data to.mzXML format file
            logging.info(get_timestamp() + ':' + 'Writing data to ' + blanka_output + '...')
            write_mzxml(blanka_output + '.mzXML', args, sample_data)


if __name__ == '__main__':
    # Start timer for processing time.
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

    # Run BLANKA.
    run_blanka(arguments)

    # Close multiprocessing pool.
    pool.close()
    pool.join()

    # Log runtime.
    logging.info(get_timestamp() + ':' + 'Total Runtime: ' + str(timeit.default_timer() - start) + ' sec')
