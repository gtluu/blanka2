from functions import *

def run_blanka(args):
    logging.info(str(datetime.datetime.now()) + ':' + 'Running BLANKA...')
    filetypes = ['.t2d', '.d', '.yep', '.baf', 'fid', '.tdf', '.wiff', '.wiff2', '.lcd', '.raw', '.unifi']
    # make output directory
    if not os.path.isdir(args['output']) and args['output'] != '':
        logging.info(str(datetime.datetime.now()) + ':' + 'Creating Output Directory...')
        os.mkdir(args['output'])

    # load in sample data and convert if necessary
    logging.info(str(datetime.datetime.now()) + ':' + 'Loading all sample data...')
    sample_file_list = load_sample_data(args, filetypes)

    # load in control data and convert if necessary
    logging.info(str(datetime.datetime.now()) + ':' + 'Loading all control data...')
    control_data = load_control_data(args, filetypes)
    # remove noise from control_data
    # control_noiseless_data == list of scans from all control datasets
    logging.info(str(datetime.datetime.now()) + ':' + 'Removing noise from control data...')
    control_noiseless_data = [pool.map(partial(noise_removal, args['signal_noise_ratio']), i)
                              for i in control_data]
    for dataset in sample_file_list:
        if args['control'] != dataset and not dataset.startswith(args['control']):
            if args['output'] == '':
                # ex: D:\folder\filename
                blanka_output = os.path.splitext(dataset)[0] + '_blanka'
            else:
                blanka_output = os.path.join(args['output'], os.path.splitext(os.path.split(dataset)[1])[0] + '_blanka')
            logging.info(str(datetime.datetime.now()) + ':' + 'Processing ' + os.path.split(dataset)[1] + '...')
            sample_data = read_mzxml(dataset)
            # noise removal when runnign full processing or only performing noise removal
            if (args['noise_removal_only'] == False and args['blank_removal_only'] == False) or \
            args['noise_removal_only'] == True:
                logging.info(str(datetime.datetime.now()) + ':' + 'Removing noise from ' + os.path.split(dataset)[1] + '...')
                sample_data['msRun']['scan'] = pool.map(partial(noise_removal, args['signal_noise_ratio']),
                                                        sample_data['msRun']['scan'])
                blanka_output += '_noise_removed'
                sample_data['msRun']['dataProcessing'].append({'@centroided': True,
                                                               'software': {'@name': 'BLANKA',
                                                                            '@type': 'noise removal',
                                                                            '@version': args['version']},
                                                               'processingOperation': {'@name': 'noise removal'}})
            # blank removal when running full processing or only performing blank removal
            if (args['noise_removal_only'] == False and args['blank_removal_only'] == False) or \
            args['blank_removal_only'] == True:
                logging.info(str(datetime.datetime.now()) + ':' + 'Removing blank spectra from ' + os.path.split(dataset)[1] + '...')
                # control_spectra == list of scan dicts for lcms, control_spectra == concensus spectrum for dd
                for control_dataset in control_noiseless_data:
                    if args['instrument'] != 'dd':
                        #sample_data['msRun']['scan'] = filter(None, [spectra_compare(args, control_dataset, i) for i in sample_data['msRun']['scan']])
                        sample_data['msRun']['scan'] = filter(None, pool.map(partial(spectra_compare, args,
                                                              control_dataset), sample_data['msRun']['scan']))
                    else:
                        for control_spectrum in control_dataset:
                            sample_data['msRun']['scan'] = filter(None, pool.map(partial(blank_removal,
                                                                  args['peak_mz_tolerance'], control_spectrum),
                                                                  sample_data['msRun']['scan']))
                blanka_output += '_blank_removed'
                sample_data['msRun']['dataProcessing'].append({'@centroided': True,
                                                               'software': {'@name': 'BLANKA',
                                                                            '@type': 'blank removal',
                                                                            '@version': args['version']},
                                                               'processingOperation': {'@name': 'blank removal'}})
            # write data to.mzXML format file
            logging.info(str(datetime.datetime.now()) + ':' + 'Writing data to ' + blanka_output + '...')
            write_mzxml(blanka_output + '.mzXML', args, sample_data)


if __name__ == '__main__':
    start = timeit.default_timer()

    arguments = get_args()

    if arguments['output'] == '':
        if os.path.isdir(arguments['sample']):
            logfile = os.path.join(arguments['sample'], 'blanka_log_' + get_datetime() + '.log')
        else:
            logfile = os.path.join(os.path.split(arguments['sample'])[0], 'blanka_log_' + get_datetime() + '.log')
    else:
        logfile = os.path.join(arguments['output'], 'blanka_log_' + get_datetime() + '.log')
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=logfile, level=logging.INFO)
    if arguments['verbose']:
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logger = logging.getLogger(__name__)

    args_check(arguments)
    arguments['msconvert_path'] = get_msconvert_path()
    arguments['version'] = '1'

    write_params(arguments, logfile)

    pool = Pool(processes=arguments['cpu'])

    run_blanka(arguments)

    pool.close()
    pool.join()

    logging.info(str(datetime.datetime.now()) + ':' + 'Total Runtime: ' + str(timeit.default_timer() - start) + ' sec')
