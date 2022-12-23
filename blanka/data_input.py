import os
from blanka.timestamp import *


# Scan directory for mzXML files.
def mzml_data_detection(directory):
    return [os.path.join(dirpath, filename) for dirpath, dirnames, filenames in os.walk(directory)
            for filename in filenames if os.path.splitext(filename)[1].lower() == '.mzml']


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
