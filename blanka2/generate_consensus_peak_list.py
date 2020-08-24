from dataset_io import *
from noise_removal import *


def generate_consensus_peak_list(args, list_of_scan_dicts):
    def get_median_rt(list_of_scan_dicts):
        return np.median([scan_dict['retentionTime'] for scan_dict in list_of_scan_dicts])

    noiseless_scan_dicts = [noise_removal(args['snr'], i) for i in list_of_scan_dicts]
    peak_lists = [i['peaks']['mz'] for i in noiseless_scan_dicts]

    # Generate temporary R script to be run from template.
    # Set working directory.
    wd = os.path.normpath(os.path.join(os.path.split(os.path.dirname(__file__))[0], 'tmp'))
    r_script = 'setwd("' + wd.replace('\\', '/') + '")\n\n'

    # Get library imports and functions.
    r_dir = os.path.normpath(os.path.join(os.path.split(os.path.dirname(__file__))[0], 'R'))
    with open(os.path.join(r_dir, 'rspeclust_template.R'), 'r') as template_file:
        r_script += template_file.read()

    # Write out peak lists to temporary .csv files and write lines in R script for each peak list.
    peak_list_variables = []
    for count, peaks in enumerate(peak_lists, 1):
        peak_list_path = os.path.normpath(os.path.join(wd, 'peaks' + str(count) + '.csv'))
        peaks.to_csv(peak_list_path, index=False, header=True)
        read_command = 'peaks' + str(count) + ' <- as.data.frame(read.table("' + peak_list_path.replace('\\', '/') +\
                       '", header=TRUE, col.names=c("mz")))\npeaks' + str(count) + ' <- as.data.frame(peaks' +\
                       str(count) + '[order(peaks' + str(count) + '$mz),])\ncolnames(peaks' + str(count) +\
                       ') <- c("mz")\n\n'
        r_script += read_command
        peak_list_variables.append('peaks' + str(count))
    r_script += 'peak_list <- list(' + ', '.join(peak_list_variables) + ')\n\n'

    # Create consensus peak list
    r_script += 'consensus <- consensusPeakList(peak_list, tol=' + str(args['precursor_mz_tol']) + ', cutoff=0.7)\n\n'
    r_script += 'write.csv(consensus, file="consensus_peak_list.csv", row.names=FALSE)\n'
    with open(os.path.join(r_dir, 'rspeclust_tmp.R'), 'w') as tmp_template_file:
        tmp_template_file.write(r_script)

    if platform.system() == 'Windows':
        subprocess.call(['R', 'CMD', 'BATCH', os.path.join(r_dir, 'rspeclust_tmp.R')],
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.call(['R', 'CMD', 'BATCH', os.path.join(r_dir, 'rspeclust_tmp.R')],
                        creationflags=subprocess.CREATE_NEW_CONSOLE, shell=True)

    consensus_peak_list = pd.read_csv(os.path.join(wd, 'consensus_peak_list.csv'))
    consensus_peak_list = pd.DataFrame({'mz': sorted(consensus_peak_list['average'].values.tolist())})

    ms_level = set([i['msLevel'] for i in list_of_scan_dicts])
    if len(ms_level) == 1:
        ms_level = list(ms_level)[0]
    else:
        # Add error message.
        return None

    return {'peaks': consensus_peak_list,
            'retentionTime': get_median_rt(list_of_scan_dicts),
            'msLevel': ms_level}