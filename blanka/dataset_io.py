import sys
import platform
import subprocess
import glob
import io
import ConfigParser
from mzxml_io import *
from generate_consensus_spectrum import *


# Scan directory for mzXML files.
def mzxml_data_detection(directory):
    return [os.path.join(dirpath, filename)
            for dirpath, dirnames, filenames in os.walk(directory)
            for filename in filenames
            if os.path.splitext(filename)[1].lower() == '.mzxml']


# Scan directory for raw vendor data formats.
def raw_data_detection(args, filetypes, directory):
    if args['instrument'] == 'dd':
        return [os.path.join(directory, filename)
                for filename in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, filename))]
    else:
        return [os.path.join(dirpath, filename)
                for dirpath, dirnames, filenames in os.walk(directory)
                for filename in filenames
                if os.path.splitext(filename)[1].lower() in filetypes]


# Convert raw vendor data files into .mzXML format files using MSConvert and default settings with peak picking.
# NOTE TO SELF make settings changeable from config file
def msconvert(args, msconvert_list):
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
                                logging.error(get_timestamp() + ':' + 'Path to msconvert.exe not found.')
                                logging.error(get_timestamp() + ':' + 'Exiting...')
                                sys.exit(1)

    msconvert_path = get_msconvert_path()

    output_file_list = []
    for filename in msconvert_list:
        if args['output'] == '':
            args['output'] = os.path.split(filename)[0]
        msconvertcmd = msconvert_path + ' ' + filename + " -o " + args['output'] + ' --mzXML --32 --mz32 ' + \
                       '--inten32 --filter "titleMaker <RunId>.<ScanNumber>.<ScanNumber>.<ChargeState>"' + \
                       ' --filter "peakPicking true 1-"'
        logging.info(get_timestamp() + ':' + msconvertcmd)
        if platform.system() == 'Windows':
            subprocess.call(msconvertcmd)
        else:
            subprocess.call(msconvertcmd, shell=True)
        if args['instrument'] == 'lcq' or args['instrument'] == 'qtof':
            output_file = os.path.split(filename)[1]
            output_file = os.path.splitext(output_file)[0]
            output_file = args['output'] + '\\' + output_file + '.mzXML'
            output_file_list.append(output_file)
        elif args['instrument'] == 'dd':
            output_file = os.path.split(filename)[1]
            output_file_list.append(args['output'] + '\\' + output_file + '.mzXML')
    return output_file_list


# Load in sample data and convert to mzXML if needed.
# LC-MS: Only converts sample files.
# MALDI-TOF Dried Droplet: Converts all files.
def load_sample_data(args, filetypes):
    if os.path.splitext(args['sample'])[1].lower() == '.mzxml':
        sample_file_list = [args['sample']]
    # Converts raw data and loads converted .mzXML file.
    elif os.path.splitext(args['sample'])[1].lower() in filetypes or os.path.split(args['sample'])[1] == 'fid':
        sample_file_list = msconvert(args, [args['sample']])
    elif os.path.splitext(args['sample'])[1].lower() == '':
        sample_file_list = mzxml_data_detection(args['sample'])
        if sample_file_list == []:
            # Detect raw data if no .mzXML files found and convert to .mzXML.
            raw_file_list = raw_data_detection(args, filetypes, args['sample'])
            # .mzXML files created in respective directories unless otherwise specified.
            sample_file_list = msconvert(args, raw_file_list)
    # Returns list of .mzXML files.
    return sample_file_list


# Load in sample data and convert to mzXML if needed.
# Currently does not take into account multiple replicates, real vs not spectra, etc.
def load_control_data(args, filetypes):
    if os.path.splitext(args['control'])[1].lower() == '.mzxml':
        control_data = read_mzxml(args['control'])
        control_data = control_data['msRun']['scan']
        return [control_data]
    elif os.path.splitext(args['control'])[1].lower() in filetypes:
        control_file = msconvert(args, [args['control']])
        control_data = read_mzxml(control_file[0])
        control_data = control_data['msRun']['scan']
        return [control_data]
    else:
        control_files = mzxml_data_detection(args['control'])
        if control_files == []:
            raw_control_files = raw_data_detection(args, filetypes, args['control'])
            control_files = msconvert(args, raw_control_files)
        control_data = [read_mzxml(control)['msRun']['scan'] for control in control_files]
        # Generate consensus spectra for MALDI-TOF DD control replicates.
        if args['instrument'] == 'dd':
            return [[generate_consensus_spectrum(args, dataset)] for dataset in control_data]
        else:
            return control_data


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
