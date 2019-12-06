# BLANKA

BLANKA is a command line tool used to remove noise and blank background signals from mass spectrometry data.

This repo contains the current development version of BLANKA. For the publication version, please see https://github.com/gtluu/blanka.

## Installation
No installation is required for use of BLANKA. Simply download the scripts and place them in the desired directory. The config.ini file must be editted to include the path to a local installation of MSConvert before usage.

## Dependencies
Python 2.7.15\
argparse 1.3.0 or higher\
pyteomics 3.5.1 or higher\
numpy 1.15.4 or higher\
pandas 0.24.0 or higher\
subprocess\
os\
sys\
multiprocessing\
functools\
copy

## Examples
Print usage information.\
```python blanka```

Perform noise and blank removal on data actinomycetes.mzXML\
```python blanka --sample E:\lcms_data\actinomycetes.mzXML --control E:\lcms_data\media_control.mzXML --instrument lcq```

Perform noise and blank removal on data found in E:\lcms_data and outputs data to E:\blanka_output\
```python blanka --sample E:\lcms_data --control E:\lcms_data\media_control.mzXML --output E:\blanka_output --instrument lcq```

Perform noise and blank removal on data found in E:\lcms_data\sample using multiple control files found in E:\lcms_data\control\
```python blanka --sample E:\lcms_data\sample --control E:\lcms_data\control --output E:\blanka_output --instrument lcq```

Convert .RAW data to .mzXML using MSConvert and perform noise and blank removal on actinomycetes.mzXML\
```python blanka --sample E:\lcms_data\actinomycetes.RAW --control E:\lcms_data\media_control.RAW --instrument lcq```

Perform noise and blank removal on data actinomycetes.mzXML with custom retention time and precursor mz tolerance\
```python blanka --sample E:\lcms_data\actinomycetes.mzXML --control E:\lcms_data\media_control.mzXML --instrument lcq --retention_time_tolerance 0.5 --peak_mz_tolerance 0.1```

Performs noise and blank removal on dried droplet maldi data using 'media_control' spots as control\
```python blanka --sample E:\maldi_data\ --control media_control --output E:\blanka_output --instrument dd```

Performs blank removal only on dried droplet maldi data using 'media_control' spots as control\
```python blanka --sample E:\maldi_data\ --control media_control --output E:\blanka_output --instrument dd --blank_removal_only True```
