import collections
import xmlschema
import pandas as pd
import os
import urllib
import base64
import struct
import re
import hashlib
import xml.etree.cElementTree as ET
from multiprocessing import Pool
from timestamp import *


# Download mzXML schema based on file namespace.
def get_mzxml_schema(schema_path):
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as mzxml_file:
            schema_path = mzxml_file.read().split('xsi:schemaLocation="')[1]
            schema_path = schema_path.split('">')[0]
            schema_path = schema_path.split(' ')[1]
    xsd_filename = os.path.split(schema_path)[-1]
    xsd = urllib.urlopen(schema_path).read().decode('utf-8')
    with open(xsd_filename, 'w') as xsd_file:
        xsd_file.write(xsd)
    return xsd_filename


# Import .mzXML file.
def read_mzxml(filepath):
    xsd = xmlschema.XMLSchema(get_mzxml_schema(filepath))

    # Convert unicode characters to string.
    def unicode_to_string(unicode):
        if isinstance(unicode, basestring):
            return str(unicode)
        elif isinstance(unicode, collections.Mapping):
            return dict(map(unicode_to_string, unicode.iteritems()))
        elif isinstance(unicode, collections.Iterable):
            return type(unicode)(map(unicode_to_string, unicode))
        else:
            return unicode

    # Use lax validation for datasets from MSConvert.
    # MSConvert causes error with strict validation due to multiple dataProcessing elements.
    mzxml_dict = unicode_to_string(xsd.to_dict(filepath, validation='lax'))[0]

    # Decode base64 encoded peaks and store in a pandas dataframe.
    def decode_peaks(peaks):
        peak_list = base64.b64decode(peaks)
        peak_list = struct.unpack('>' + str(len(peak_list) / 4) + 'L', peak_list)
        mz_list = [struct.unpack('f', struct.pack('I', i))[0] for i in peak_list[::2]]
        int_list = [struct.unpack('f', struct.pack('I', i))[0] for i in peak_list[1::2]]
        return pd.DataFrame(list(zip(mz_list, int_list)), columns=['mz', 'intensity'])

    for scan_dict in mzxml_dict['msRun']['scan']:
        try:
            scan_dict['peaks'][0]['$'] = decode_peaks(scan_dict['peaks'][0]['$'])
        except KeyError:
            # Skip scan if there are no peaks.
            pass
        scan_dict['nameValue'] = {}

    return mzxml_dict


# Output data to .mzXML file.
def write_mzxml(filename, args, mzxml_dict):
    xsd = xmlschema.XMLSchema(get_mzxml_schema(mzxml_dict['@xsi:schemaLocation'].split(' ')[1]))

    def update_msrun_metadata(mzxml_dict):
        # msRun attrib
        mzxml_dict['msRun']['@scanCount'] = long(len(mzxml_dict['msRun']['scan']))
        ret_time_list = [float(i['@retentionTime'][2:-1]) for i in mzxml_dict['msRun']['scan']]
        mzxml_dict['msRun']['@startTime'] = 'PT' + str(min(ret_time_list)) + 'S'
        mzxml_dict['msRun']['@endTime'] = 'PT' + str(max(ret_time_list)) + 'S'
        return mzxml_dict

    # Encode peaks to bse64 encoding.
    def encode_peaks(peaks):
        mz_list = peaks['mz'].values.tolist()
        int_list = peaks['intensity'].values.tolist()
        peak_list = [None] * (len(mz_list) + len(int_list))
        peak_list[::2], peak_list[1::2] = mz_list, int_list
        peak_list = [struct.unpack('I', struct.pack('f', i))[0] for i in peak_list]
        peak_list = struct.pack('>' + str(len(peak_list)) + 'L', *peak_list)
        return base64.b64encode(peak_list)

    # Update scan metadata based on modified spectra.
    def update_scan_metadata(scan_dict):
        try:
            scan_dict['@peaksCount'] = long(len(scan_dict['peaks'][0]['$']))
        except:
            logging.exception(get_timestamp() + ':' + 'Error writing peaksCount...')
        try:
            scan_dict['@lowMz'] = min(scan_dict['peaks'][0]['$']['mz'].values.tolist())
        except:
            logging.exception(get_timestamp() + ':' + 'Error writing lowMz...')
        try:
            scan_dict['@highMz'] = max(scan_dict['peaks'][0]['$']['mz'].values.tolist())
        except:
            logging.exception(get_timestamp() + ':' + 'Error writing highMz...')
        try:
            scan_dict['@basePeakMz'] = max(scan_dict['peaks'][0]['$'].values.tolist(), key=lambda x: x[1])[0]
        except:
            logging.exception(get_timestamp() + ':' + 'Error writing basePeakMz...')
        try:
            scan_dict['@basePeakIntensity'] = max(scan_dict['peaks'][0]['$']['intensity'].values.tolist())
        except:
            logging.exception(get_timestamp() + ':' + 'Error writing basePeakIntensity...')
        try:
            scan_dict['@totIonCurrent'] = sum(scan_dict['peaks'][0]['$']['intensity'].values.tolist())
        except:
            logging.exception(get_timestamp() + ':' + 'Error writing totIonCurrent...')
        try:
            scan_dict['peaks'][0]['$'] = encode_peaks(scan_dict['peaks'][0]['$'])
        except:
            logging.exception(get_timestamp() + ':' + 'Error writing peaks...')
        # Remove any temporary data stored in nameValue slots.
        del scan_dict['nameValue']
        return scan_dict

    pool = Pool(processes=args['cpu'])
    mzxml_dict = update_msrun_metadata(mzxml_dict)
    mzxml_dict['msRun']['scan'] = pool.map(update_scan_metadata, mzxml_dict['msRun']['scan'])
    pool.close()
    pool.join()

    # Use lax validation for datasets from MSConvert.
    # MSConvert causes error with strict validation due to multiple dataProcessing elements.
    encoded_element = xsd.elements['mzXML'].encode(mzxml_dict, validation='lax', unordered=True)[0]
    mzxml_tree = ET.tostring(encoded_element, encoding='ISO-8859-1', method='xml')

    # identify/write index, indexOffset, and sha1 data
    # Write index elements.
    scan_offsets = [i.start() for i in re.finditer('<scan', mzxml_tree)]
    mzxml_dict['index']['offset'] = [{'@id': long(count), '$': long(i)}
                                     for count, i in enumerate(scan_offsets, start=1)]
    encoded_element = xsd.elements['mzXML'].encode(mzxml_dict, validation='lax', unordered=True)[0]
    mzxml_tree = ET.tostring(encoded_element, encoding='ISO-8859-1', method='xml')

    # Write index offset element.
    mzxml_dict['indexOffset'] = long([i.start() for i in re.finditer('<index', mzxml_tree)][0])
    encoded_element = xsd.elements['mzXML'].encode(mzxml_dict, validation='lax', unordered=True)[0]
    mzxml_tree = ET.tostring(encoded_element, encoding='ISO-8859-1', method='xml')

    # Write SHA1 element.
    sha1 = mzxml_tree[:mzxml_tree.find('</indexOffset>') + len('</indexOffset>')]
    sha1 = sha1.encode()
    mzxml_dict['sha1'] = hashlib.sha1(sha1).hexdigest()
    encoded_element = xsd.elements['mzXML'].encode(mzxml_dict, validation='lax', unordered=True)[0]
    mzxml_tree = ET.tostring(encoded_element, encoding='ISO-8859-1', method='xml')

    # Change boolean string values to binary integers instead.
    mzxml_tree = mzxml_tree.replace('centroided="true"', 'centroided="1"')
    mzxml_tree = mzxml_tree.replace('centroided="false"', 'centroided="0"')
    mzxml_tree = mzxml_tree.replace('="true"', '="1"')
    mzxml_tree = mzxml_tree.replace('="false"', '="0"')

    # Write out XML string to .mzXML file.
    with open(filename, 'w') as mzxml_file:
        mzxml_file.write(mzxml_tree)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
