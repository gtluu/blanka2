# BLANKA2

BLANKA2 is a command line tool used to remove noise and blank background signals from mass spectrometry data. It takes mzML files as input and returns modified mzML files without MS/MS files that were found in the specified blanks. Blank detection is performed using MS/MS clustering through [falcon](https://github.com/bittremieux/falcon). Importantly, full scan MS data is not affected.

This repo contains the current development version of BLANKA actively being worked on. For the publication version, please see [here](https://github.com/gtluu/blanka).

If you use BLANKA2, please cite us:

```
Jessica L. Cleary, Gordon T. Luu, Emily C. Pierce, Rachel J. Dutton, Laura M. Sanchez. (2019). BLANKA: an Algorithm for Blank Subtraction in Mass Spectrometry of Complex Biological Samples. *Journal of The American Society for Mass Spectrometry*; 30, 1426-1434. doi: 10.1007/s13361-019-02185-8.
```

## Installation

BLANKA2 is available for use in Linux. Due to the falcon's (and therefore BLANKA2's) use of the Faiss library, which lacks a Windows implementation, BLANKA2 is not available for native Windows use. However, users may run BLANKA2 and other Linux based software in the Windows Subsystem for Linux environment.

#### Install Anaconda on Linux

1. Download and install Anaconda for [Linux](https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh). 
Follow the prompts to complete installation. Anaconda3-2021.11 for Linux is used as an example here.
```
wget https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
bash /path/to/Anaconda3-2021.11-Linux-x86_64.sh
```
2. Add ```anaconda3/bin``` to PATH.
```
export PATH=$PATH:/path/to/anaconda3/bin
```

#### Set Up ```conda env```

3. Create a conda instance. You must be using Python 3.8.
```
conda create -n blanka python=3.8
```
4. Activate conda environment.
```
conda activate blanka
```

#### Install BLANKA2

5. Download BLANKA2 by cloning the Github repo (you will need to have [Git](https://git-scm.com/downloads) and 
ensure that the option to enable symbolic links was checked during installation). It may be necessary to explicitly
allow for the use of symbolic links by adding the ```-c core.symlinks=true``` parameter on Windows.
```
git clone https://www.github.com/gtluu/blanka2
or
git clone -c core.symlinks=true https://www.github.com/gtluu/blanka2
```
6. Install dependencies.
```
# BLANKA2 dependencies
pip install -r /path/to/blanka2/requirements.txt
```

## Usage

To use BLANKA2, run it via the command line. An basic example can be found below:
```
python /path/to/blanka2/blanka.py --sample_input /path/to/sample/mzML/files --blank_input /path/to/blank/mzML/files
```

Parameters to optimize clustering using falcon can also be passed through BLANKA2. To see a full list of parameters, run:
```
python /path/to/blanka2/blanka.py --help
```
