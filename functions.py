import xml.etree.cElementTree as ET
import xmlschema, argparse, urllib, collections
import sys, os, platform, subprocess, io
import re, base64, struct, hashlib, glob
import pandas, numpy
import datetime, timeit, ConfigParser, logging
from multiprocessing import Pool, cpu_count
from functools import partial

def unicode_to_string(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(unicode_to_string, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(unicode_to_string, data))
    else:
        return data

def get_mzxml_schema(schema_path):
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as mzxml_file:
            schema_path = mzxml_file.read().split('xsi:schemaLocation="')[1].split('">')[0].split(' ')[1]
    xsd_filename = os.path.split(schema_path)[-1]
    xsd = urllib.urlopen(schema_path).read().decode('utf-8')
    with open(xsd_filename, 'w') as xsd_file:
        xsd_file.write(xsd)
    return xsd_filename

def decode_peaks(peaks):
    peak_list = base64.b64decode(peaks)
    peak_list = struct.unpack('>' + str(len(peak_list) / 4) + 'L', peak_list)
    mz_list = [struct.unpack('f', struct.pack('I', i))[0] for i in peak_list[::2]]
    int_list = [struct.unpack('f', struct.pack('I', i))[0] for i in peak_list[1::2]]
    return pandas.DataFrame(list(zip(mz_list, int_list)), columns=['mz', 'intensity'])

def encode_peaks(peaks):
    mz_list = peaks['mz'].values.tolist()
    int_list = peaks['intensity'].values.tolist()
    peak_list = [None] * (len(mz_list) + len(int_list))
    peak_list[::2], peak_list[1::2] = mz_list, int_list
    peak_list = [struct.unpack('I', struct.pack('f', i))[0] for i in peak_list]
    peak_list = struct.pack('>' + str(len(peak_list)) + 'L', *peak_list)
    return base64.b64encode(peak_list)

def read_mzxml(filepath):
    xsd = xmlschema.XMLSchema(get_mzxml_schema(filepath))
    mzxml_dict = unicode_to_string(xsd.to_dict(filepath, validation='lax'))[0]
    for scan_dict in mzxml_dict['msRun']['scan']:
        try:
            scan_dict['peaks'][0]['$'] = decode_peaks(scan_dict['peaks'][0]['$'])
        except KeyError:
            pass
        scan_dict['nameValue'] = {}
    return mzxml_dict

def update_dataset_metadata(mzxml_dict):
    # msRun attrib
    mzxml_dict['msRun']['@scanCount'] = long(len(mzxml_dict['msRun']['scan']))
    ret_time_list = [float(i['@retentionTime'][2:-1]) for i in mzxml_dict['msRun']['scan']]
    mzxml_dict['msRun']['@startTime'] = 'PT' + str(min(ret_time_list)) + 'S'
    mzxml_dict['msRun']['@endTime'] = 'PT' + str(max(ret_time_list)) + 'S'
    return mzxml_dict

def update_scan_metadata(scan_dict):
    try:
        scan_dict['@peaksCount'] = long(len(scan_dict['peaks'][0]['$']))
    except:
        pass
    try:
        scan_dict['@lowMz'] = min(scan_dict['peaks'][0]['$']['mz'].values.tolist())
    except:
        pass
    try:
        scan_dict['@highMz'] = max(scan_dict['peaks'][0]['$']['mz'].values.tolist())
    except:
        pass
    try:
        scan_dict['@basePeakMz'] = max(scan_dict['peaks'][0]['$'].values.tolist(), key=lambda x: x[1])[0]
    except:
        pass
    try:
        scan_dict['@basePeakIntensity'] = max(scan_dict['peaks'][0]['$']['intensity'].values.tolist())
    except:
        pass
    try:
        scan_dict['@totIonCurrent'] = sum(scan_dict['peaks'][0]['$']['intensity'].values.tolist())
    except:
        pass
    try:
        scan_dict['peaks'][0]['$'] = encode_peaks(scan_dict['peaks'][0]['$'])
    except:
        pass
    # running list: quality_score, binned_peaks, dot_product_score, consensus
    '''if isinstance(scan_dict['nameValue'], dict):
        scan_dict['nameValue'] = [value for key, value in scan_dict['nameValue']]
        for key, value in scan_dict['nameValue']:
            if isinstance(scan_dict['nameValue'][key]['@value'], pandas.DataFrame):
                scan_dict['nameValue'][key]['@value'] = encode_peaks(scan_dict['nameValue'][key]['@value'])
            else:
                scan_dict['nameValue'][key]['@value'] = str(scan_dict['nameValue'][key]['@value'])'''
    del scan_dict['nameValue']
    return scan_dict

def write_mzxml(filename, args, mzxml_dict):
    xsd = xmlschema.XMLSchema(get_mzxml_schema(mzxml_dict['@xsi:schemaLocation'].split(' ')[1]))
    pool = Pool(processes=args['cpu'])
    mzxml_dict = update_dataset_metadata(mzxml_dict)
    mzxml_dict['msRun']['scan'] = pool.map(update_scan_metadata, mzxml_dict['msRun']['scan'])
    pool.close()
    pool.join()
    # lax validation for datasets from msconvert
    encoded_element = xsd.elements['mzXML'].encode(mzxml_dict, validation='lax', unordered=True)[0]
    mzxml_tree = ET.tostring(encoded_element, encoding='ISO-8859-1', method='xml')
    # identify/write index, indexOffset, and sha1 data
    scan_offsets = [i.start() for i in re.finditer('<scan', mzxml_tree)]
    mzxml_dict['index']['offset'] = [{'@id': long(count), '$': long(i)}
                                     for count, i in enumerate(scan_offsets, start=1)]
    encoded_element = xsd.elements['mzXML'].encode(mzxml_dict, validation='lax', unordered=True)[0]
    mzxml_tree = ET.tostring(encoded_element, encoding='ISO-8859-1', method='xml')
    mzxml_dict['indexOffset'] = long([i.start() for i in re.finditer('<index', mzxml_tree)][0])
    encoded_element = xsd.elements['mzXML'].encode(mzxml_dict, validation='lax', unordered=True)[0]
    mzxml_tree = ET.tostring(encoded_element, encoding='ISO-8859-1', method='xml')
    mzxml_dict['sha1'] = hashlib.sha1(mzxml_tree[:mzxml_tree.find('</indexOffset>') + len('</indexOffset>')].encode()).hexdigest()
    encoded_element = xsd.elements['mzXML'].encode(mzxml_dict, validation='lax', unordered=True)[0]
    mzxml_tree = ET.tostring(encoded_element, encoding='ISO-8859-1', method='xml')
    # fix centroided="true" --> centroided="1"
    mzxml_tree = mzxml_tree.replace('centroided="true"', 'centroided="1"')
    mzxml_tree = mzxml_tree.replace('centroided="false"', 'centroided="0"')
    with open(filename, 'w') as mzxml_file:
        mzxml_file.write(mzxml_tree)

def get_args():
    parser = argparse.ArgumentParser()
    # required args
    parser.add_argument('--sample', help="sample input directory/file", required=True, type=str)
    parser.add_argument('--control', help="control input file path with '.mzXML' file extension (lcq/qtof) or \
                                                name of control sample spot (dd)", required=True, type=str)
    parser.add_argument('--instrument', help="instrument/experiment (choose 'lcq', 'qtof', 'dd'", required=True,
                        type=str)
    # optional args
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

def args_check(args):
    # check sample and control path
    if not os.path.exists(args['sample']):
        logging.error(str(datetime.datetime.now()) + ':' + 'Sample path does not exist...')
        logging.error(str(datetime.datetime.now()) + ':' + 'Exiting...')
        sys.exit(1)
    if not os.path.exists(args['control']):
        logging.error(str(datetime.datetime.now()) + ':' + 'Control path does not exist...')
        logging.error(str(datetime.datetime.now()) + ':' + 'Exiting...')
        sys.exit(1)
    # check blank removal thresholds
    if args['ms1_threshold'] > 1:
        logging.error(str(datetime.datetime.now()) + ':' + 'MS1 Threshold must be <= 1...')
        logging.error(str(datetime.datetime.now()) + ':' + 'Exiting...')
    if args['ms2_threshold'] > 1:
        logging.error(str(datetime.datetime.now()) + ':' + 'MS2 Threshold must be <= 1...')
        logging.error(str(datetime.datetime.now()) + ':' + 'Exiting...')
    # check --cpu
    if args['cpu'] >= cpu_count():
        logging.error(str(datetime.datetime.now()) + ':' + 'Number of threads specified exceeds number of available threads...')
        logging.error(str(datetime.datetime.now()) + ':' + 'Your computer has ' + str(cpu_count() - 1) + ' usable threads...')
        logging.error(str(datetime.datetime.now()) + ':' + 'Exiting...')
        sys.exit(1)
    # check --instrument
    if not args['instrument'] == 'lcq' and not args['instrument'] == 'qtof' and not args['instrument'] == 'dd':
        logging.error(str(datetime.datetime.now()) + ':' + 'Invalid instrument...')
        logging.error(str(datetime.datetime.now()) + ':' + 'Exiting...')
        sys.exit(1)
    # check noise and blank removal only options
    if args['noise_removal_only'] and args['blank_removal_only']:
        logging.error(str(datetime.datetime.now()) + ':' + '--noise_removal_only and --blank_removal_only both cannot be selected at once...')
        logging.error(str(datetime.datetime.now()) + ':' + 'Exiting...')
        sys.exit(1)


def get_datetime():
    dt = str(datetime.datetime.now())
    dt = dt.replace(' ', '_')
    dt = dt.replace(':', '-')
    dt = dt.replace('.', '-')
    return dt


def write_params(args, logfile):
    with open(os.path.join(os.path.split(logfile)[0], 'parameters_' + get_datetime() + '.txt'), 'a') as params:
        for key, value in args.iteritems():
            params.write('[' + str(key) + ']' + '\n' + str(value) + '\n')


# scan directory for .mzXML files
def mzxml_data_detection(directory):
    return [os.path.join(dirpath, filename) for dirpath, dirnames, filenames in os.walk(directory)
            for filename in filenames if os.path.splitext(filename)[1].lower() == '.mzxml']


def raw_data_detection(args, filetypes, directory):
    if args['instrument'] == 'dd':
        return [os.path.join(directory, filename) for filename in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, filename))]
    else:
        return [os.path.join(dirpath, filename) for dirpath, dirnames, filenames in os.walk(directory)
                for filename in filenames if os.path.splitext(filename)[1].lower() in filetypes]


def get_msconvert_path():
    # try to get msconvert.exe from default Windows Proteowizard installation path
    try:
        msconvert_path = glob.glob('C:\\Program Files\\Proteowizard\\*\\msconvert.exe')[0]
        if os.path.isfile(msconvert_path):
            return msconvert_path
        else:
            raise IndexError
    except IndexError:
        with open(os.path.dirname(__file__) + '/config.ini', 'r') as config_file:
            config = config_file.read()
        config_parser = ConfigParser.RawConfigParser(allow_no_value=True)
        config_parser.readfp(io.BytesIO(config))
        for param in config_parser.sections():
            if param == 'msconvert':
                for option in config_parser.options(param):
                    if option == 'path':
                        msconvert_path = config_parser.get(param, option)
                        if os.path.isfile(msconvert_path):
                            return msconvert_path
                        else:
                            logging.error(str(datetime.datetime.now()) + ':' + 'Path to msconvert.exe not found.')
                            logging.error(str(datetime.datetime.now()) + ':' + 'Exiting...')
                            sys.exit(1)


# convert raw data files detected into .mzXML format using MSConvert and default Sanchez Lab settings
# NOTE TO SELF make settings changeable from config file
def msconvert(args, msconvert_list):
    output_file_list = []
    for filename in msconvert_list:
        if args['output'] == '':
            args['output'] = os.path.split(filename)[0]
        msconvertcmd = args['msconvert_path'] + ' ' + filename + " -o " + args['output'] + ' --mzXML --32 --mz32\
                                    --inten32 --filter "titleMaker <RunId>.<ScanNumber>.<ScanNumber>.<ChargeState>"\
                                    --filter "peakPicking true 1-2"'
        logging.info(str(datetime.datetime.now()) + ':' + msconvertcmd)
        if platform.system() == 'Windows':
            subprocess.call(msconvertcmd)
        else:
            subprocess.call(msconvertcmd, shell=True)
        if args['instrument'] == 'lcq' or args['instrument'] == 'qtof':
            output_file_list.append(args['output'] + '\\' + os.path.splitext(os.path.split(filename)[1])[0] + '.mzXML')
        elif args['instrument'] == 'dd':
            output_file_list.append(args['output'] + '\\' + os.path.split(filename)[1] + '.mzXML')
    return output_file_list

def calculate_relative_intensity(max_intensity, intensity):
    return (intensity / max_intensity) * 100

def ppm_to_mz(error, mass):
    return (error / (10**6)) * mass

def mz_to_ppm(error, mass):
    return (error / mass) * (10**6)

# quality score based on signal to noise ratio
def calculate_quality_score(scan_dict):
    # list of intensities in a spectrum
    intensity_list = scan_dict['peaks'][0]['$']['intensity'].values.tolist()
    # 2nd to 6th highest peaks in spectrum
    highest_peaks = sorted(intensity_list, reverse=True)[1:6]
    # quality score = average of 2nd to 6th most intense peaks / media intensity
    quality_score = numpy.mean(highest_peaks) / numpy.median(sorted(intensity_list))
    scan_dict['nameValue']['quality_score'] = {'@name': 'qualityScore', '@value': quality_score}
    return scan_dict

def get_tolerance_values():
    pass

# create bins for dot product calculation
def get_binned_peaks(list_of_scan_dicts):
    concat_df = pandas.DataFrame()
    for scan_dict in list_of_scan_dicts:
        concat_df = pandas.concat([concat_df, scan_dict['peaks'][0]['$']])
    bins = numpy.arange(int(round(min(concat_df['mz'].values.tolist())))-2,
                        int(round(max(concat_df['mz'].values.tolist())))+2, step=0.2)
    for scan_dict in list_of_scan_dicts:
        binned_peaks = scan_dict['peaks'][0]['$'].groupby(pandas.cut(scan_dict['peaks'][0]['$']['mz'],
                                                                     bins=bins)).aggregate(sum)
        scan_dict['nameValue']['binned_peaks'] = {'@name': 'binned_peaks', '@value': binned_peaks}
    return list_of_scan_dicts

def dot_product_calculation(ref_scan_dict, scan_dict):
    try:
        # see if binned peaks exists
        ref_scan_dict['nameValue']['binned_peaks']['@value']
        scan_dict['nameValue']['binned_peaks']['@value']
    except KeyError:
        ref_scan_dict['nameValue']['binned_peaks'] = {'@name': 'binned_peaks', '@value': ref_scan_dict['peaks'][0]['$']}
        scan_dict['nameValue']['binned_peaks'] = {'@name': 'binned_peaks', '@value': scan_dict['peaks'][0]['$']}
    # get list of intensity values for each scan
    ref_int = ref_scan_dict['nameValue']['binned_peaks']['@value']['intensity'].values.tolist()
    intensities = scan_dict['nameValue']['binned_peaks']['@value']['intensity'].values.tolist()
    if len(ref_int) == len(intensities):
        numerator = sum([i*j for i, j in zip(ref_int, intensities)])
        denominator = (sum([i**2 for i in ref_int]) * sum([i**2 for i in intensities]))**0.05
        scan_dict['nameValue']['dot_product_score'] = {'@name': 'dotProductScore', '@value': numerator / denominator}
    else:
        scan_dict['nameValue']['dot_product_score'] = {'@name': 'dotProductScore', '@value': 0}
    return scan_dict

def multi_merge_asof(tolerance, list_of_scan_dicts):
    for count, scan_dict in enumerate(list_of_scan_dicts):
        # generate consensus spectrum in first/top scan
        if count == 0:
            list_of_scan_dicts[0]['nameValue']['consensus'] = {'@name': 'consensusSpectrum',
                                                               '@value': scan_dict['peaks'][0]['$']}
        else:
            # tolerance = args['peak_mz_tolerance]
            consensus_spectrum = pandas.merge_asof(list_of_scan_dicts[0]['nameValue']['consensus']['@value'],
                                                   scan_dict['peaks'][0]['$'], on='mz', tolerance=tolerance,
                                                   direction='nearest', suffixes=['_' + str(count-1), '_' + str(count)])
            list_of_scan_dicts[0]['nameValue']['consensus'] = {'@name': 'consensusSpectrum',
                                                               '@value': consensus_spectrum}
    # return first/top scan with newly generated consensus spectrum
    return list_of_scan_dicts[0]

def cluster_replicates(args, ranked_scan_dicts):
    pool = Pool(processes=args['cpu'])
    list_of_clusters = []
    count = 0
    # repeat clustering process until no scans with dot product score under 0.6 present
    while True:
        # top ranked scan dict based on quality score
        top_ranked_scan_dict = ranked_scan_dicts[0]
        top_ranked_scan_dict['nameValue']['dot_product_score']['@value'] = 1
        # calculate dot product scores for each scan
        dot_product_results = pool.map(partial(dot_product_calculation, top_ranked_scan_dict), ranked_scan_dicts[1:])
        over_threshold = [top_ranked_scan_dict] + [scan_dict for scan_dict in dot_product_results
                                                   if scan_dict['nameValue']['dot_product_score']['@value'] >= 0.6]
        list_of_clusters.append((over_threshold, count))
        ranked_scan_dicts = [scan_dict for scan_dict in dot_product_results
                             if scan_dict['namevalue']['dot_product_score']['@value'] < 0.6]
        count += 1
        if len(ranked_scan_dicts) == 0:
            break
    num_scans_largest_cluster = max([len(cluster) for cluster in list_of_clusters])
    list_largest_clusters = [cluster for cluster in list_of_clusters if len(cluster) == num_scans_largest_cluster]
    pool.close()
    pool.join()
    # return largest cluster of scan_dicts
    return sorted(list_largest_clusters, key=lambda x: x[1])[0][0]

def align_replicates(args, cluster):
    pool = Pool(processes=args['cpu'])
    for scan_dict in cluster:
        scan_dict['peaks'][0]['$']['ion'] = scan_dict['peaks'][0]['$']['mz'].values.tolist()
        intensities = scan_dict['peaks'][0]['$']['intensity'].values.tolist()
        scan_dict['peaks'][0]['$']['rel_inten'] = pool.map(partial(calculate_relative_intensity, max(intensities)),
                                                           intensities)
    # each scan placed first to account for differences in peaks due to merge_asof using left outer join
    list_cluster_combos = [[cluster[i]] + [j for j in cluster if not j == cluster[i]] for i in range(0, len(cluster))]
    pool.close()
    pool.join()
    # return list_of_scan_dicts with consensus spectrum generated
    return [multi_merge_asof(args['peak_mz_tolerance'], cluster) for cluster in list_cluster_combos]

def preprocess_consensus_spectrum(scan_dict):
    ion_col = [i for i in scan_dict['nameValue']['consensus']['@value'].columns.values.tolist() if i.startswith('ion')]
    rel_inten_col = [i for i in scan_dict['nameValue']['consensus']['@value'].columns.values.tolist()
                     if i.startswith('rel_inten')]
    scan_dict['nameValue']['consensus']['@value']['ave_mz'] = scan_dict['nameValue']['consensus']['@value']\
                                                                       [ion_col].mean(axis=1, skipna=True)
    # implement weighted mean later?
    scan_dict['nameValue']['consensus']['@value']['ave_mz'] = scan_dict['nameValue']['consensus']['@value'] \
                                                                       [rel_inten_col].mean(axis=1, skipna=True)
    scan_dict['nameValue']['consensus']['@value'] = scan_dict['nameValue']['consensus']['@value']\
                                                    [scan_dict['nameValue']['consensus']['@value']['ave_rel_inten']!=0]
    scan_dict['nameValue']['consensus']['@value'] = scan_dict['nameValue']['consensus']['@value']\
                                                             [['ave_mz', 'ave_rel_inten']]
    return scan_dict

def multi_merge(cluster):
    for count, scan_dict in enumerate(cluster):
        if count == 0:
            consensus_df = scan_dict['nameValue']['consensus']['@value']
        else:
            consensus_df = pandas.merge(consensus_df, scan_dict['nameValue']['consensus']['@value'],
                                        on='ave_mz', how='outer', suffixes=('_' + str(count-1), '_' + str(count)))
    ave_rel_inten = [i for i in consensus_df.columns.values.tolist() if i.startswith('ave_rel_inten')]
    consensus_df['intensity'] = consensus_df[ave_rel_inten].mean(axis=1, skipna=True)
    return consensus_df[['ave_mz', 'intensity']].rename(columns={'ave_mz': 'mz', 'intensity': 'intensity'})

def generate_consensus_spectrum(args, list_of_scan_dicts):
    pool = Pool(processes=args['cpu'])
    ranked_scan_dicts = sorted(pool.map(calculate_quality_score, list_of_scan_dicts), key=lambda x:
                               x['nameValue']['quality_score']['@value'], reverse=True)
    binned_scan_dicts = get_binned_peaks(ranked_scan_dicts)
    largest_cluster = cluster_replicates(args, binned_scan_dicts)
    aligned_cluster = align_replicates(args, largest_cluster)
    preprocessed_cluster = pool.map(preprocess_consensus_spectrum, aligned_cluster)
    pool.close()
    pool.join()
    return {'peaks': [{'$': multi_merge(preprocessed_cluster)}]}

# load in sample data; converts all files (sample and control) if needed
# loads .mzXML data if found or converts raw data if not; only converts sample data if lcq/qtof; converts all if dd
# loads .mzXML file
def load_sample_data(args, filetypes):
    if os.path.splitext(args['sample'])[1].lower() == '.mzxml':
        sample_file_list = [args['sample']]
    # converts and loads .RAW file
    elif os.path.splitext(args['sample'])[1].lower() in filetypes or os.path.split(args['sample'])[1] == 'fid':
        sample_file_list = msconvert(args, [args['sample']])
    elif os.path.splitext(args['sample'])[1].lower() == '':
        sample_file_list = mzxml_data_detection(args['sample'])
        if sample_file_list == []:
            # detect raw data if no .mzXML files found and convert to .mzXML
            raw_file_list = raw_data_detection(args, filetypes, args['sample'])
            # .mzXML files created in respective directories unless otherwise provided
            # list of .mzXML files
            sample_file_list = msconvert(args, raw_file_list)
    return sample_file_list

# load control dataset
# does not take into account multiple replicates, real vs not spectra, etc.
def load_control_data(args, filetypes):
    if os.path.splitext(args['control'])[1].lower() == '.mzxml':
        return [read_mzxml(args['control'])['msRun']['scan']]
    elif os.path.splitext(args['control'])[1].lower() in filetypes:
        control_file = msconvert(args, [args['control']])
        return [read_mzxml(control_file[0])['msRun']['scan']]
    else:
        control_files = mzxml_data_detection(args['control'])
        if control_files == []:
            raw_control_files = raw_data_detection(args, filetypes, args['control'])
            control_files = msconvert(args, raw_control_files)
        control_data = [read_mzxml(control)['msRun']['scan'] for control in control_files]
        # generate consensus spectra for maldi control replicates
        if args['instrument'] == 'dd':
            return [[generate_consensus_spectrum(args, dataset)] for dataset in control_data]
        else:
            return control_data

# remove noise from dataset using average of 5% lowest intensity peaks as noise level and user defined SNR
def noise_removal(snr, scan_dict):
    try:
        peaks = scan_dict['peaks'][0]['$']
        peaks = peaks[peaks['intensity'] != 0]
        sorted_intensities = sorted(peaks['intensity'].values.tolist())
        lowest_sorted_intensities = sorted_intensities[:int(round((len(sorted_intensities) * 0.05)))]
        if len(lowest_sorted_intensities) != 0:
            spectrum_noise = sum(lowest_sorted_intensities) / len(lowest_sorted_intensities)
        else:
            spectrum_noise = min(peaks['intensity'].values.tolist())
        scan_dict['peaks'][0]['$'] = peaks[peaks['intensity'] >= (snr * spectrum_noise)]
    except KeyError:
        pass
    return scan_dict

# remove control spectrum peaks from sample spectrum if m/z within specified tolerance for MS1 spectra
# remove sample spectrum if corresponding spectrum is found in control dataset for MS^n spectra
# return None if control spectrum empty
# return sample spectrum if sample spectrum empty
# return None if control spectrum matched peaks make up <= MS1 threshold of number of sample peaks in MS1
# return None if control spectrum matched peaks make up <= MS2 threshold of number of sample peaks in MS2
def blank_removal(peak_mz_tolerance, ms1_threshold, ms2_threshold, control_spectrum, sample_spectrum):
    try:
        if sample_spectrum['peaks'][0]['$'].empty:
            return sample_spectrum
        blank_subtracted_df = pandas.merge_asof(sample_spectrum['peaks'][0]['$'].sort_values('mz'),
                                                control_spectrum['peaks'][0]['$'].sort_values('mz'), on='mz',
                                                tolerance=peak_mz_tolerance, direction='nearest').fillna(0)
        blank_subtracted_df = blank_subtracted_df[blank_subtracted_df['intensity_y'] == 0]
        if int(sample_spectrum['@msLevel']) == 1:
            threshold = ms1_threshold
        elif int(sample_spectrum['@msLevel']) >= 2:
            threshold = ms2_threshold
        if (sum(blank_subtracted_df['intensity_x'].values.tolist()) /
        sum(sample_spectrum['peaks'][0]['$']['intensity'].values.tolist())) <= threshold:
            blank_subtracted_df = blank_subtracted_df[['mz', 'intensity_x']].rename(columns={'mz': 'mz',
                                                                                             'intensity_x': 'intensity'})
            sample_spectrum['peaks'][0]['$'] = blank_subtracted_df
            return sample_spectrum
    except KeyError:
        return sample_spectrum

# select control spectrum for LC-MS data bsed on MS mode, retention time and precursor m/z
def select_control_spectrum_lcms(args, control_spectra, sample_spectrum):
    # search by retention time for MS1
    if int(sample_spectrum['@msLevel']) == 1:
        control_spectra_list = [i for i in control_spectra if int(i['@msLevel']) == 1
                                if (float(i['@retentionTime'][2:-1]) + args['retention_time_tolerance']) >=
                                float(sample_spectrum['@retentionTime'][2:-1]) >=
                                (float(i['@retentionTime'][2:-1]) - args['retention_time_tolerance'])]
    # search by retention time and precursor m/z for MS^n
    elif int(sample_spectrum['@msLevel']) >= 2:
        control_spectra_list = [i for i in control_spectra if int(i['@msLevel']) >= 2 if not len(i['precursorMz']) > 1
                                if (float(i['@retentionTime'][2:-1]) + args['retention_time_tolerance']) >=
                                float(sample_spectrum['@retentionTime'][2:-1]) >=
                                (float(i['@retentionTime'][2:-1]) - args['retention_time_tolerance']) and
                                (float(i['precursorMz'][0]['$']) + args['precursor_mz_tolerance']) >=
                                float(sample_spectrum['precursorMz'][0]['$']) >=
                                (float(i['precursorMz'][0]['$']) - args['precursor_mz_tolerance'])]
    # return None if no matching spectra found
    if len(control_spectra_list) != 0:
        # return best match if more than one spectra found meeting criteria
        # best match based on closest retention time and precursor m/z
        if len(control_spectra_list) > 1:
            if int(sample_spectrum['@msLevel']) == 1:
                # calculate difference in retention time
                ret_time_diff = [abs(float(sample_spectrum['@retentionTime'][2:-1]) - float(i['@retentionTime'][2:-1]))
                                 for i in control_spectra_list]
                # list of control spectra iwht lowest difference in retention time
                control_spectra_list = [control_spectra_list[i] for i, j in enumerate(ret_time_diff)
                                        if j == min(ret_time_diff)]
                if len(control_spectra_list) > 1:
                    # return spectrum most similar to sample based on dot product score
                    return sorted([dot_product_calculation(sample_spectrum, i) for i in control_spectra_list],
                                  key=lambda x: x['nameValue']['dot_product_score']['@value'], reverse=True)
                elif len(control_spectra_list) == 1:
                    return control_spectra_list[0]
            elif int(sample_spectrum['@msLevel']) >= 2:
                # calculate difference in retention time and precursor mz
                ret_time_diff = [abs(float(sample_spectrum['@retentionTime'][2:-1]) - float(i['@retentionTime'][2:-1]))
                                 for i in control_spectra_list]
                precursor_mz_diff = [abs(float(sample_spectrum['precursorMz'][0]['$']) -
                                         float(i['precursorMz'][0]['$'])) for i in control_spectra_list]
                control_spectra_list2 = [control_spectra_list[i]
                                         for i, j in enumerate(zip(ret_time_diff, precursor_mz_diff))
                                         if j[0] == min(ret_time_diff) and j[1] == min(precursor_mz_diff)]
                if not control_spectra_list2:
                    # return spectrum most similar to sample based on dot product score (changed to generate consensus spectrum)
                    return sorted([dot_product_calculation(sample_spectrum, i) for i in control_spectra_list],
                                  key=lambda x: x['nameValue']['dot_product_score']['@value'], reverse=True)
                else:
                    if len(control_spectra_list2) > 1:
                        # return spectrum most similar to sample based on dot product score (changed to generate consensus spectrum)
                        return sorted([dot_product_calculation(sample_spectrum, i) for i in control_spectra_list2],
                                      key=lambda x: x['nameValue']['dot_product_score']['@value'], reverse=True)[0]
                    elif len(control_spectra_list2) == 1:
                        # return control spectrum with lowest difference in retention time and precursor mz
                        return control_spectra_list2[0]
        elif len(control_spectra_list) == 1:
            # return control spectra if only one found
            return control_spectra_list[0]

# select control spectrum and remove blanks
def spectra_compare(args, control_spectra, sample_spectrum):
    control_spectrum = select_control_spectrum_lcms(args, control_spectra, sample_spectrum)
    if not control_spectrum:
        return sample_spectrum
    else:
        return blank_removal(args['peak_mz_tolerance'], args['ms1_threshold'], args['ms2_threshold'], control_spectrum,
                             sample_spectrum)

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
