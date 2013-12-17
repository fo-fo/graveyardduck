# GraveyardDuck #

GraveyardDuck is a simple tool to decompress and recompress graphic files used
in the old Famicom Disk System game *Dracula II: Noroi no Fuuin*, better known
as *Castlevania: Simon's Quest* in the US.

It also works on *Ai Senshi Nicol*, *Rampart* and possibly other Konami games.


## Compression Teardown ##

The above games use a very simple variant of run-length encoding (RLE), a
simple compression scheme used in many early bitmap graphic formats.

Konami's RLE scheme can be expressed in a few simple rules:

* if(*n* < 128) then write the following byte *n* times to the decompressed
  stream
* if(*n* > 128) then write the following *n* bytes to the decompressed stream
* if(*n* == 128) then write the following 256 bytes
* if(*n* == 255) then terminate compression

In practice, the case of (*n* == 255) is almost impossible to encounter given
the nature of the graphics this scheme is designed to compress.


## Usage ##

Assuming the parameters:

* FILENAME: The file into/from which data will be compressed/decompressed
* POSITION: Offset where compressed data is located or will be stored
* BLOCK: The file to which decompressed data will be written or from which
  it will be sourced

### Decompression ###

> graveduck.py -d [FILENAME] [POSITION] [BLOCK]

### Compression ###

> graveduck.py -c [FILENAME] [POSITION] [BLOCK]


## Authors ##

** Derrick Sobodash **

* <http://derrick.sobodash.com/>
* <https://twitter.com/sobodash/>
* <http://weibo.com/sobodash/>


## Copyright ##

Copyright &copy; 2012, 2013 Derrick Sobodash

