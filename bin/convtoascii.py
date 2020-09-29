#!/usr/bin/env python3
import os.path
import sys

for arg in sys.argv[1:]:
    print(os.path.abspath(arg))

def conv(input, output):
    nonascii = bytearray(range(0x80, 0x100))
    nonascii +=b'0x22'
    with open(input,'rb') as infile, open(output,'wb') as outfile:
        for line in infile:
            outfile.write(line.translate(None, nonascii))

if __name__== "__main__":
    if len(sys.argv) < 3:
        print("convtoascii input output")
        exit(-1)
    conv(sys.argv[1],sys.argv[2])
