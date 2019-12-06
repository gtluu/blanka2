import timeit
from functions import *

def run_blanka(args):
    filetypes = ['.t2d', '.d', '.yep', '.baf', 'fid', '.tdf', '.wiff', '.wiff2', '.lcd', '.raw', '.unifi']
    # make output directory
    if not os.path.isdir(args['output']) and args['output'] != '':
        os.mkdir(args['output'])

    # load in sample data and convert if necessary
    # control_list only used if MALDI DD dataset
    sample_file_list = load_sample_data(args, filetypes)

    # load in control data and convert if necessary
    control_data = load_control_data(args, filetypes)
    # remove noise from control_data
    # control_noiseless_data == list of scans from all control datasets
    control_noiseless_data = [pool.map(partial(noise_removal, args['signal_noise_ratio']), i)
                              for i in control_data]
    for dataset in sample_file_list:
        if args['control'] != dataset and not dataset.startswith(args['control']):
            if args['output'] == '':
                # ex: D:\folder\filename
                blanka_output = os.path.splitext(dataset)[0] + '_blanka'
            else:
                blanka_output = os.path.join(args['output'], os.path.splitext(os.path.split(dataset)[1])[0] + '_blanka')
            print 'Processing ' + os.path.split(dataset)[1] + '...'
            sample_data = read_mzxml(dataset)
            # noise removal when runnign full processing or only performing noise removal
            if (args['noise_removal_only'] == False and args['blank_removal_only'] == False) or \
            args['noise_removal_only'] == True:
                print 'Removing Noise...'
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
                print 'Removing Blank Spectra...'
                # control_spectra == list of scan dicts for lcms, control_spectra == concensus spectrum for dd
                for control_dataset in control_noiseless_data:
                    if args['instrument'] != 'dd':
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
            print 'Writing to ' + blanka_output + '.mzXML'
            write_mzxml(blanka_output + '.mzXML', args, sample_data)

if __name__ == '__main__':
    start = timeit.default_timer()

    arguments = get_args()
    args_check(arguments)
    arguments['version'] = '1'

    pool = Pool(processes=arguments['cpu'])

    run_blanka(arguments)

    pool.close()
    pool.join()

    print 'Total Runtime: ' + str(timeit.default_timer() - start) + ' sec'
