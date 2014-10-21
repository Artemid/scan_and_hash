__author__ = 'Artem Nurgaliev artemy.nurgaliev@gmail.com'

import os
import sys
from os import path
import re
import struct
import hashlib
import threading
import json
import sqlite3 as lite


def read_file(name):
	data = open('myfile.zip', 'rb').read()
	start = 0
	for i in range(3):	# show the first 3 file headers
		start += 14
		fields = struct.unpack('<IIIHH', data[start:start+16])
		crc32, comp_size, uncomp_size, filenamesize, extra_size = fields

		start += 16
		filename = data[start:start+filenamesize]
		start += filenamesize
		extra = data[start:start+extra_size]
		print filename, hex(crc32), comp_size, uncomp_size

		start += extra_size + comp_size	# skip to the next header


def hashfile(afile, hasher, blocksize=65536):
	buf = afile.read(blocksize)
	while len(buf) > 0:
		hasher.update(buf)
		buf = afile.read(blocksize)
	return hasher.hexdigest()


def scan_package(pkg_name, packages):
	root = os.walk(path.join(pkg_name, "images"))

	blocks = []

	for cur_dir, dirs, files in root:
		# [(fname, hashfile(open(fname, 'rb'), hashlib.sha256())) for fname in files]
		for name in files:
			fname = path.join(cur_dir, name)
			digest = hashfile(open(fname, 'rb'), hashlib.md5())
			#print("File: %s - %s" % (fname, digest))

			block = {}
			block["name"] = fname
			block["crc"] = digest
			blocks.append(block)

	packages.append(blocks)


class ScanPackages(threading.Thread):
	def __init__(self, dir_name):
		threading.Thread.__init__(self)
		self.dir_name = dir_name
		self.packages = []

	def run(self):
		fname = r'.*_meta\.xml'

		root = os.walk(self.dir_name)
		print("Scan started: %s" % self.dir_name)
		for cur_dir, dirs, files in root:
			for name in files:
				#print("File: %s" % join(cur_dir, name))
				if re.match(fname, name):
					#print("File: %s" % join(cur_dir, name))
					scan_package(cur_dir, self.packages)
		print("Scan complete")

		output_file = "output.json"
		print("Writing JSON data: %s" % output_file)
		data = open(output_file, "w")
		data.write(json.dumps(self.packages))
		data.close()
		print("Write colmplete")


def main_scan():
	print("Application started")

	background = ScanPackages("../PAPG/build/papgg5/cdimage")
	background.start()

	print("Patience...")

	background.join()


def main_json():
	data = open("output.json", "r")
	packages = json.loads(data.read())
	data.close()

	for files in packages:
		for file in files:
			print("File: %s - %s" % (file["name"], file["crc"]))


def main_sqlite():
	print("testing sqlite")

	con = lite.connect('packages.db')

	with con:
		cur = con.cursor()
		cur.execute("CREATE TABLE Cars(Id INT, Name TEXT, Price INT)")
		cur.execute("INSERT INTO Cars VALUES(1,'Audi',52642)")
		cur.execute("INSERT INTO Cars VALUES(2,'Mercedes',57127)")
		cur.execute("INSERT INTO Cars VALUES(3,'Skoda',9000)")
		cur.execute("INSERT INTO Cars VALUES(4,'Volvo',29000)")
		cur.execute("INSERT INTO Cars VALUES(5,'Bentley',350000)")
		cur.execute("INSERT INTO Cars VALUES(6,'Citroen',21000)")
		cur.execute("INSERT INTO Cars VALUES(7,'Hummer',41400)")
		cur.execute("INSERT INTO Cars VALUES(8,'Volkswagen',21600)")


if __name__ == "__main__":
	main_scan()
	#main_json()
	#main_sqlite()
