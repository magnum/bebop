#!/usr/bin/python
"""
Converts a Parrot Bebop blackbox recording into a .csv file.

@author: Matthew Lloyd (github@matthewlloyd.net)
"""

import optparse
import os
import struct


class BlackboxFileReader(object):
	def __init__(self, filename):
		self.filename = filename
		self._read_file()

	def _read_file(self):
		# Read the file.
		contents = open(self.filename, 'rb').read()

		# Extract the JSON header.
		data_index = contents.index('-- Data\x0a')
		header_lines = contents[:data_index].split('\x0a')
		packets = contents[data_index + len('-- Data\x0a'):]
		print data_index + len('-- Data\x0a')

		# Parse the header.
		self.packet_length = 0
		self.column_indices = {}
		for line in header_lines:
			line = line.strip()
			# Extract the column information.
			if line.startswith('nentries:'):
				self.nentries = int(line.split(':')[1])
				continue
			if line.startswith('datasize:'):
				self.datasize = int(line.split(':')[1])
				continue
			if line.startswith('titles:'):
				self.titles = map(lambda s: s.strip(), line.split(':')[1].split(','))
				continue
		assert self.datasize == 8
		assert len(self.titles) == self.nentries
		self.packet_length = self.datasize * self.nentries
		assert self.packet_length > 0

		self.struct_format = '<' + 'd' * self.nentries

		for i, title in enumerate(self.titles):
			self.column_indices[title] = i

		# Unpack the packets
		self.packets = []
		i = 0
		while len(packets) - i >= self.packet_length:
			packet = packets[i:i + self.packet_length]
			packet_fields = struct.unpack(self.struct_format, packet)
			self.packets.append(packet_fields)
			i += self.packet_length

		# TODO: warn if there is data left over


def make_csv(reader):
	f = reader.filename
	if os.path.exists(f + '.csv'):
		return
	print 'Creating CSV file for %s' % (f,)
	c = open(f + '.csv', 'w')
	c.write(','.join(c for c in reader.titles) + '\n')
	for packet in reader.packets:
		c.write(','.join(str(c) for c in packet) + '\n')
	c.close()


def main():
	parser = optparse.OptionParser()
	parser.add_option("-d", "--dir", default=None, dest="dir", help="directory to search for *.pud files")
	for flag in ('csv', ):
		parser.add_option("--%s" % flag, action="store_true", dest=flag, default=True)
		parser.add_option("--no-%s" % flag, action="store_false", dest=flag)

	(options, args) = parser.parse_args()

	files = list(args)
	if options.dir is not None:
		files = files + list(os.path.join(options.dir, f) for f in os.listdir(options.dir) if f.endswith('.pud'))

	for filename in files:
		print "Processing %s..." % (filename,)
		reader = BlackboxFileReader(filename)
		if options.csv:
			make_csv(reader)


if __name__ == '__main__':
	main()
