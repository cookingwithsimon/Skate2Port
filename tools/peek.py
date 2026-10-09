"""Read big-endian words from the dumped Skate 2 image: peek.py <bin> <addr> [count]"""
import struct, sys
data = open(sys.argv[1], 'rb').read()
addr = int(sys.argv[2], 16); n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
for i in range(n):
    a = addr + 4 * i
    print(f"{a:08X}: {struct.unpack('>I', data[a - 0x82000000:a - 0x82000000 + 4])[0]:08X}")
