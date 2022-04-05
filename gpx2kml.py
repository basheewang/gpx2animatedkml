# -*- coding: utf-8 -*-

"""This is a script to convert gpx to animated kml."""

import xml.etree.ElementTree as ET
import argparse
import numpy as np
# import sys


def parse_gpx(gpx_file):
    """To get the longitude and lagtitude values from a gpx file."""
    tree = ET.parse(gpx_file)
    root = tree.getroot()
    track_name_elem = trkpt_name = [elem.tag for elem in root.iter()
                                    if 'name' in elem.tag][0]
    track_name = [i.text for i in root.iter(track_name_elem)][0]

    trkpt_name = [elem.tag for elem in root.iter() if 'trkpt' in elem.tag][0]
    ele_name = [elem.tag for elem in root.iter() if 'ele' in elem.tag][0]

    coord = list()
    for trkpt in root.iter(trkpt_name):
        # print(trkpt.tag, trkpt.attrib)
        pt_coord = list(trkpt.attrib.values())
        # pt_coord.append('0')
        # print(pt_coord)
        pt_coord.reverse()
        coord.append(pt_coord)

    for idx, ele in enumerate(root.iter(ele_name)):
        pt_ele = ele.text
        coord[idx].append(pt_ele)
    return track_name, coord


def print_kml_header(file_name, track_name):
    """To print KML header."""
    print(r'<?xml version="1.0" encoding="UTF-8"?>',
          file=file_name)
    print('<kml xmlns="http://www.opengis.net/kml/2.2" '
          'xmlns:gx="http://www.google.com/kml/ext/2.2" '
          'xmlns:kml="http://www.opengis.net/kml/2.2" '
          'xmlns:atom="http://www.w3.org/2005/Atom">',
          file=file_name)
    print('  <Document>\n    <name>', track_name, '</name>\n',
          '    <open>1</open>', sep='',
          file=file_name)
    print('''
        <Style id="line-style">
          <LineStyle>
            <color>bf00aaff</color>
            <width>5</width>
          </LineStyle>
        </Style>''',
          file=file_name)


def print_kml_lookup(file_name, coord, range_value):
    """Generate kml file lookup segment."""
    coord_mean = np.mean(np.float_(coord), axis=0)
    print('\n    <LookAt>', file=file_name)
    print('      <longitude>', coord_mean[0],
          '</longitude>', sep="", file=file_name)
    print('      <latitude>', coord_mean[1],
          '</latitude>', sep="", file=file_name)
    print('      <altitude>', coord_mean[2],
          '</altitude>', sep="", file=file_name)
    print('      <range>', range_value, '</range>', sep="", file=file_name)
    print('      <gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>',
          file=file_name)
    print('    </LookAt>', file=file_name)


def print_kml_gx_animate(file_name, coord, wait_time=0.02):
    """Gennerate animate segment."""
    print('''
    <gx:Tour>
      <name>Double-click here to start tour</name>
      <gx:Playlist>

        <gx:Wait> <gx:duration>1</gx:duration></gx:Wait>
    ''', end="", file=file_name)
    id = 0
    for i in range(len(coord) - 1):
        print('''
            <gx:AnimatedUpdate>
              <Update>
                <Change><Placemark targetId="''',
              id,
              '''"><visibility>1</visibility></Placemark></Change>
              </Update>
            </gx:AnimatedUpdate>

            <gx:Wait><gx:duration>''',
              wait_time,
              '''</gx:duration></gx:Wait>
        ''', sep="", end="", file=file_name)
        id += 1
    print('''
          </gx:Playlist>
        </gx:Tour>

    ''', file=file_name)


def print_kml_placemark(file_name, coord):
    """Generate kml placemark segment."""
    print('''
        <Folder>
          <name>Path segments</name>

          <Style>
            <ListStyle>
              <listItemType>checkHideChildren</listItemType>
            </ListStyle>
          </Style>

    ''', file=file_name)
    id = 0
    for i in range(len(coord) - 1):
        id += 1
        print('          <Placemark id="', id, '">', sep="", file=file_name)
        print('            <name>', id, '</name>',
              sep="", end="", file=file_name)
        print('''
                <visibility>0</visibility>
                <styleUrl>#line-style</styleUrl>
                <LineString>
                  <tessellate>1</tessellate>
                  <coordinates>\n''', end="", file=file_name)
        print('                ', ','.join(x for x in coord[id - 1]),
              ' ',
              ','.join(x for x in coord[id]), sep="", end="", file=file_name)
        print('''
                  </coordinates>
                </LineString>
              </Placemark>
        ''', end="", file=file_name)


def print_kml_footer(file_name):
    """Generate kml footer."""
    print('''
        </Folder>
      </Document>
    </kml>
    ''', end="", file=file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Covert gpx to kml')
    parser.add_argument("-i", "--gpx_file", help="Input a gpx file to convert")
    parser.add_argument("-r", "--range_value", nargs='?', const=1, type=int,
                        help="Range value for google earth.", default=3500)
    parser.add_argument("-w", "--wait_time", nargs='?', const=0.02, type=float,
                        help="Range value for google earth.", default=3500)
    args = parser.parse_args()
    # print(args.gpx_file)
    track_name, track_coord = parse_gpx(args.gpx_file)
    print('There are total',
          len(track_coord),
          'geographic points in this gpx file.')
    output_file = str(args.gpx_file).split('.')[0] + '.kml'
    f = open(output_file, 'w')
    # sys.stdout = f
    print_kml_header(f, track_name)
    print_kml_lookup(f, track_coord, args.range_value)
    print_kml_gx_animate(f, track_coord, args.wait_time)
    print_kml_placemark(f, track_coord)
    print_kml_footer(f)
    f.close()
    print("OK")
