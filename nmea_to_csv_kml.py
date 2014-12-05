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


class NMEAFileReader(object):
	def __init__(self, filename):
		self.filename = filename
		self._read_file()

	def _read_file(self):
		self.columns = ['Lat', 'Lon', 'Alt']
		self.column_indices = dict( (v, k) for (k, v) in enumerate(self.columns) )
		self.packets = []

		# Process each line.
		for line in open(self.filename, 'r'):
			if not line.startswith('$'):
				continue
			parts = line.split('*')[0].split(',')
			if parts[0] == '$GNGNS':
				utc, lat, lat_d, lon, lon_d, mode, num_svs, hdop, height, sep, age, ref = parts[1:13]
				self.packets.append( (
					float(lat) * (1 if lat_d == 'N' else -1) / 100.0,
					float(lon) * (1 if lat_d == 'E' else -1) / 100.0,
					float(height)
				) )


def make_csv(reader):
	f = reader.filename
	if os.path.exists(f + '.csv'):
		return
	print 'Creating CSV file for %s' % (f,)
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
	print 'Creating KML for %s' % (f,)
	coord = []
	for packet in reader.packets:
		if packet[reader.column_indices['Lat']] == 0.0:
			continue
		coord.append( (
			packet[reader.column_indices['Lon']],
			packet[reader.column_indices['Lat']],
			packet[reader.column_indices['Alt']] * 3.28,  # m -> feet
			) )

	kml = simplekml.Kml()
	gxtrack = kml.newgxtrack(name='track', altitudemode='relativeToGround')
	gxtrack.newgxcoord(coord)
	kml.save(f_kml)


def main():
	parser = optparse.OptionParser()
	parser.add_option("-d", "--dir", default=None, dest="dir", help="directory to search for *.nmea files")
	for flag in ('kml', 'csv'):
		parser.add_option("--%s" % flag, action="store_true", dest=flag, default=True)
		parser.add_option("--no-%s" % flag, action="store_false", dest=flag)

	(options, args) = parser.parse_args()

	files = list(args)
	if options.dir is not None:
		files = files + list(os.path.join(options.dir, f) for f in os.listdir(options.dir) if f.endswith('.nmea'))

	for filename in files:
		print "Processing %s..." % (filename,)
		reader = NMEAFileReader(filename)
		if options.kml:
			make_kml(reader)
		if options.csv:
			make_csv(reader)


if __name__ == '__main__':
	main()
