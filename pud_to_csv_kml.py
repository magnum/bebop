#!/usr/bin/python
"""
Converts a Parrot Bebop .pud log file into a .csv file and a .kml file.
Requires the simplekml Python module for KML support.

@author: Matthew Lloyd (github@matthewlloyd.net)
"""

import json
import optparse
import os
import struct


class PUDFileReader(object):
    def __init__(self, filename):
        self.filename = filename
        self._read_file()

    def _read_file(self):
        # Read the file.
        contents = open(self.filename, 'rb').read()

        # Extract the JSON header.
        null_terminator_index = contents.index(b'\x00')
        header_json = contents[:null_terminator_index]
        packets = contents[null_terminator_index + 1:]

        # Parse the header.
        header = json.loads(header_json)
        details_headers = header['details_headers']

        # Extract the column information.
        self.columns = []
        self.struct_format = '<'
        self.packet_length = 0
        self.column_indices = {}
        for i, details_header in enumerate(details_headers):
            detail_name = details_header['name']
            detail_type = details_header['type']
            detail_size = int(details_header['size'])

            if detail_type == 'integer':
                # assume signed
                if detail_size == 1:
                    detail_format = 'b'
                elif detail_size == 2:
                    detail_format = 'h'
                elif detail_size == 4:
                    detail_format = 'i'
                elif detail_size == 8:
                    detail_format = 'q'
                else:
                    raise Exception('Unsupported integer size %d for field %s' % (detail_size, detail_name))
            elif detail_type == 'boolean':
                if detail_size == 1:
                    detail_format = '?'
                else:
                    raise Exception('Unsupported boolean size %d for field %s' % (detail_size, detail_name))
            elif detail_type == 'double':
                if detail_size == 8:
                    detail_format = 'd'
                else:
                    raise Exception('Unsupported double size %d for field %s' % (detail_size, detail_name))
            elif detail_type == 'float':
                if detail_size == 4:
                    detail_format = 'f'
                else:
                    raise Exception('Unsupported float size %d for field %s' % (detail_size, detail_name))
            else:
                raise Exception('Unsupported detail type %s for field %s' % (detail_type, detail_name))

            self.columns.append((detail_name, detail_type, detail_size, detail_format))
            self.struct_format += detail_format
            self.packet_length += detail_size

            self.column_indices[detail_name] = i

        # Unpack the packets
        self.packets = []
        while len(packets) >= self.packet_length:
            packet = packets[:self.packet_length]
            packets = packets[self.packet_length:]
            packet_fields = struct.unpack(self.struct_format, packet)
            self.packets.append(packet_fields)

        # TODO: warn if there is data left over


def make_csv(reader):
	f = reader.filename
	if os.path.exists(f + '.csv'):
		return
	print('Creating CSV file for %s' % (f,))
	c = open(f + '.csv', 'w')
	c.write(','.join(c[0] for c in reader.columns) + '\n')
	for packet in reader.packets:
		c.write(','.join(str(c) for c in packet) + '\n')
	c.close()


def make_kml(reader):
	import simplekml
	f = reader.filename
	f_kml = f + '.kml'
	if os.path.exists(f_kml):
		return
	print('Creating KML for %s' % (f,))
	coord = []
	for packet in reader.packets:
		if packet[reader.column_indices['product_gps_longitude']] == 0.0:
			continue
		coord.append( (
			packet[reader.column_indices['product_gps_longitude']],
			packet[reader.column_indices['product_gps_latitude']],
			packet[reader.column_indices['altitude']] / 1000.0,  # millimeters to meters
			) )

	kml = simplekml.Kml()
	gxtrack = kml.newgxtrack(name='track', altitudemode='relativeToGround')
	gxtrack.newgxcoord(coord)
	kml.save(f_kml)


def main():
	parser = optparse.OptionParser()
	parser.add_option("-d", "--dir", default=None, dest="dir", help="directory to search for *.pud files")
	for flag in ('kml', 'csv'):
		parser.add_option("--%s" % flag, action="store_true", dest=flag, default=True)
		parser.add_option("--no-%s" % flag, action="store_false", dest=flag)

	(options, args) = parser.parse_args()

	files = list(args)
	if options.dir is not None:
		files = files + list(os.path.join(options.dir, f) for f in os.listdir(options.dir) if f.endswith('.pud'))

	for filename in files:
		print("Processing %s..." % (filename,))
		reader = PUDFileReader(filename)
		if options.kml:
			make_kml(reader)
		if options.csv:
			make_csv(reader)


if __name__ == '__main__':
	main()
