#!/usr/bin/python2.7

'''
GraveyardDuck

A tool decompress and recompress graphic files in the old Famicom Disk System
game Dracula II: Noroi no Fuuin, better known as Simon's Quest in the US.
It also works on Ai Senshi Nicol, and possibly other Konami games.

Version:   1.3
Author:    Derrick Sobodash <derrick@sobodash.com>
Copyright: (c) 2012 Derrick Sobodash
Web site:  http://derrick.sobodash.com/
License:   BSD License <http://opensource.org/licenses/bsd-license.php>
'''

'''
Change Log

1.3 - Cleaned up a couple lines and added decompression support for the
      special 0x80 code, which is used to include a 256-byte block in which
      no compression is possible.

1.2 - Fixed the int() command used to sanitize input. You will now be able to
      specify an offset using octal (0712) or hexadecimal (0xbeef).

1.1 - Fixed a potential (highly unlikely) overflow if more than 126 bytes pass
      before any RLE can be achieved.
      Fixed output message when no input is given. Old line was necro-ripped
      from another project of mine. Oops!
'''

# Initialize the program
try:
	import sys
	import glob
	import os
	import re
	from struct import *
	import time
	from stat import *
	
except ImportError, err:
	print "Could not load %s module." % (err)
	raise SystemExit

print "GraveyardDuck 1.3 (cli)\nCopyright (c) 2012 Derrick Sobodash\n"

'''
konamidec():

This function decompresses a block of the game that is stored in the Konami
compression format. The format is a simple RLE scheme:

* value < 0x80 = repeat the next byte n times
* value > 0x80 = write the following n bytes
* value = 0x80 = write the following 256 bytes [TODO!]

Compression is terminated when a value of 0xff is read into the file.
'''
def konamidec(file, offset):
	print "Opening " + file + " ..."
	f = open(file, "rb")
	print "[Seeked to " + str(offset) + "]"
	f.seek(offset)
	decomp = ""
	
	# This loop will run forever till an 0xff breaks it.
	print "Decompressing data ..."
	while file:
		control = ord(f.read(1))
		
		if control == 0xff:
			break
		
		# If byte is bigger than 0x80, grab bytes
		if control > 0x80:
			decomp += f.read(control - 0x80) 
		
		# If byte is 0x80, write the next 256 bytes
		elif control == 0x80:
			decomp += f.read(0x100)
		
		# Otherwise, write the next byte n times
		else:
			temp = f.read(1)
			for i in range(0, control):
				decomp += temp
				
	f.close()
	return decomp

'''
konamicod():

UP, UP, DOWN, DOWN, LEFT, RIGHT, LEFT, RIGHT, B, A, START
'''
def konamicod(block):
	print "Spooling " + block + " ..."
	f = open(block, "rb")
	size = os.stat(block)[ST_SIZE]
	stream = f.read(size)
	f.close()
	
	# Start the compressed stream
	comp = ""
	
	i = 0
	last = None
	running = None
	
	print "Compressing block data ..."
	while i < len(stream):
		char = stream[i]
		last  = i
		count = 0
		while i < len(stream) and stream[i] == char:
			count = count + 1
			i     = i + 1
		if count > 2:
			if running != None:
				comp = comp + chr(0x80 + len(running)) + running
			if count > 0x7f:
				while count > 0x7f:
					comp = comp + chr(0x7f) + char
					count = count - 0x7f
			comp = comp + chr(count) + char
			running = None
		else:
			if running == None:
				running = stream[last:i]
			else:
				# A "gotcha" for 1.1. There was no check in place in case
				# there were more than 0x7c bytes between RLEs. Need for this
				# fix was highly unlikely, but better safe than sorry.
				# Why 0x7c? because 0x7c + 2 from a possible failed RLE gives
				# us 0xfe, which is still safe.
				if len(running) > 0xfc - 0x80:
					comp = comp + chr(0x80 + len(running)) + running
					running = None
				else:
					running = running + stream[last:i]
	
	if running != None:
		comp = comp + chr(0x80 + len(running)) + running
	
	return comp + "\xff"

# No input, prompt user
if len(sys.argv) < 2:
	print "No input action given. Run with -h for a list of options."
	raise SystemExit

# Help message
elif sys.argv[1] == "-h" or sys.argv[1] == "-help":
	print "Decompress Usage:"
	print "  graveduck.py -d [FILENAME] [POSITION] [BLOCK]"
	print "Compress Usage:"
	print "  graveduck.py -c [FILENAME] [POSITION] [BLOCK]"
	print "Where:"
	print "  FILENAME = Source file containing compressed data"
	print "  POSITION = Offset in source file where compressed block begins"
	print "  BLOCK    = Decompressed data"
	raise SystemExit

# Super happy fun time!
if len(sys.argv) == 5:
	file   = sys.argv[2]
	offset = int(sys.argv[3], 0)
	block  = sys.argv[4]
	
	if sys.argv[1] == "-d":
		decomp = konamidec(file, offset)
		print "[Expanded " + str(len(decomp)) + "b from " + file + "]"
		o = open(block, "w")
		print "Writing to " + block + " ..."
		o.write(decomp)
		o.close()
	
	elif sys.argv[1] == "-c":
		comp = konamicod(block)
		print "[Compressed " + str(os.stat(block)[ST_SIZE]) + "b to " + str(len(comp)) + "b]"
		print "Opening " + file + " ..."
		o = open(file, "r+w")
		o.seek(offset)
		print "[Seeked to " + str(offset) + "]"
		print "Inserting data ..."
		o.write(comp)
		o.close()
	
	else:
		print "DIVISION BY 0 OH SH--"
	
	print "~Fin"
