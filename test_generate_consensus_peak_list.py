from blanka2.generate_consensus_peak_list import *
from blanka2.noise_removal import *

args = {'snr': 4,
        'precursor_mz_tol': 1}

alpha_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'data', 'peaks', 'alpha.peaks'))
beta_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'data', 'peaks', 'beta.peaks'))
delta_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'data', 'peaks', 'delta.peaks'))
gamma_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'data', 'peaks', 'gamma.peaks'))

alpha = pd.read_csv(alpha_path, header=None)
alpha.columns = ['mz']
beta = pd.read_csv(beta_path, header=None)
beta.columns = ['mz']
delta = pd.read_csv(delta_path, header=None)
delta.columns = ['mz']
gamma = pd.read_csv(gamma_path, header=None)
gamma.columns = ['mz']

scan_dicts = [{'peaks': alpha}, {'peaks': beta}, {'peaks': delta}, {'peaks': gamma}]

generate_consensus_peak_list(args, scan_dicts)
