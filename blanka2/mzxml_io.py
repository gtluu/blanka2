from lxml import etree as et
import re
import hashlib
import base64
import struct
import pandas as pd


def read_mzxml(sample_file):
    def decode_peaks(peaks, precision):
        peak_list = base64.b64decode(peaks)
        peak_list = struct.unpack('>' + str(len(peak_list) / 4) + 'L', peak_list)
        mz_list = [struct.unpack('f', struct.pack('I', i))[0] for i in peak_list[::2]]
        int_list = [struct.unpack('f', struct.pack('I', i))[0] for i in peak_list[1::2]]
        return pd.DataFrame(list(zip(mz_list, int_list)), columns=['mz', 'intensity'])

    mzxml_data = et.parse(sample_file).getroot()
    ns = mzxml_data.tag[:mzxml_data.tag.find('}') + 1]
    list_of_scan_elements = mzxml_data.findall('.//' + ns + 'scan')
    # get scan num, ms level, precursor, rt, peaks
    list_of_scan_dicts = []
    for scan in list_of_scan_elements:
        # Get precursor m/z information.
        precursor_list = scan.findall('.//' + ns + 'precursorMz')
        precursor_list = [{'precursorMz': float(i.text)} for i in precursor_list]
        # Get and decode peak information.
        peaks_element = scan.find('.//' + ns + 'peaks')
        if peaks_element.text:
            # Append scan_dict.
            scan_dict = {'num': int(scan.attrib['num']),
                         'msLevel': int(scan.attrib['msLevel']),
                         'retentionTime': float(scan.attrib['retentionTime'][2:-1]),
                         'precursorMz': precursor_list,
                         'lowMz': float(scan.attrib['lowMz']),
                         'highMz': float(scan.attrib['highMz']),
                         'peaks': decode_peaks(str(peaks_element.text), int(peaks_element.attrib['precision']))}
            list_of_scan_dicts.append(scan_dict)
    return list_of_scan_dicts


def modify_mzxml(blanka_output, list_of_scan_dicts, sample_file):
    # Load in .mzXML file.
    mzxml_data = et.parse(sample_file).getroot()
    ns = mzxml_data.tag[:mzxml_data.tag.find('}') + 1]

    # Remove old index, indexOffset, and SHA1.
    mzxml_data.remove(mzxml_data.find(ns + 'index'))
    mzxml_data.remove(mzxml_data.find(ns + 'indexOffset'))
    mzxml_data.remove(mzxml_data.find(ns + 'sha1'))

    # Remove scans that are in the list of spectra to be removed (i.e. spectra that matched a blank spectrum).
    for scan_dict in list_of_scan_dicts:
        for child in mzxml_data.iter():
            if child.tag == ns + 'scan':
                if child.attrib['num'] == str(scan_dict['num']):
                    child.getparent().remove(child)

    # Get all scan elements and list of retention times.
    scan_elements = mzxml_data.findall('.//' + ns + 'scan')
    ret_time_list = [float(scan.attrib['retentionTime'][2:-1]) for scan in scan_elements]

    # Update msRun metadata.
    for child in mzxml_data.iter():
        if child.tag == ns + 'msRun':
            child.attrib['scanCount'] = str(len(scan_elements))
            child.attrib['startTime'] = 'PT' + str(min(ret_time_list)) + 'S'
            child.attrib['endTime'] = 'PT' + str(max(ret_time_list)) + 'S'

    # Write out temporary .mzXML file.
    mzxml_tree = et.tostring(mzxml_data, encoding='ISO-8859-1', method='xml', pretty_print=True)
    with open(blanka_output, 'w') as output_file:
        output_file.write(mzxml_tree)
    parser = et.XMLParser(remove_blank_text=True)
    mzxml_data = et.parse(blanka_output, parser).getroot()

    # Update index elements.
    scan_offsets = [i.start() for i in re.finditer('<scan', mzxml_tree)]
    scan_nums = [i['num'] for i in read_mzxml(blanka_output)]
    index_element = et.SubElement(mzxml_data, ns + 'index', attrib={'name': 'scan'})
    for offset, scan_num in zip(scan_offsets, scan_nums):
        offset_element = et.SubElement(index_element, ns + 'offset', attrib={'id': scan_num})
        offset_element.text = str(offset)

    # Rewrite temporary mzxml_tree.
    mzxml_tree = et.tostring(mzxml_data, encoding='ISO-8859-1', method='xml', pretty_print=True)
    with open(blanka_output, 'w') as output_file:
        output_file.write(mzxml_tree)
    mzxml_data = et.parse(blanka_output, parser).getroot()

    # Update indexOffset element
    index_offset = [i.start() for i in re.finditer('<index', mzxml_tree)][0]
    index_offset_element = et.SubElement(mzxml_data, ns + 'indexOffset')
    index_offset_element.text = str(index_offset)

    # Rewrite temporary mzxml_tree.
    mzxml_tree = et.tostring(mzxml_data, encoding='ISO-8859-1', method='xml', pretty_print=True)
    with open(blanka_output, 'w') as output_file:
        output_file.write(mzxml_tree)
    mzxml_data = et.parse(blanka_output, parser).getroot()

    # Update SHA1 element.
    sha1 = mzxml_tree[:mzxml_tree.find('</indexOffset>') + len('</indexOffset>')]
    sha1 = sha1.encode()
    sha1 = hashlib.sha1(sha1).hexdigest()
    sha1_element = et.SubElement(mzxml_data, ns + 'sha1')
    sha1_element.text = str(sha1)

    # Write out Element object to .mzXML file.
    mzxml_tree = et.tostring(mzxml_data, encoding='ISO-8859-1', method='xml', pretty_print=True)
    with open(blanka_output, 'w') as output_file:
        output_file.write(mzxml_tree)
