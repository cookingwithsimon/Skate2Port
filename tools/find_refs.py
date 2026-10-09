"""Find data words / lis+addi pairs that reference an address: find_refs.py <bin> <addr>"""
import struct, sys
data = open(sys.argv[1], 'rb').read(); target = int(sys.argv[2], 16)
pat = struct.pack('>I', target)
i = data.find(pat)
while i >= 0:
    print(f"data ref at {0x82000000 + i:08X}"); i = data.find(pat, i + 1)
hi = (target + 0x8000) >> 16 & 0xFFFF; lo = target & 0xFFFF
for off in range(0, len(data) - 4, 4):
    w = struct.unpack_from('>I', data, off)[0]
    if w >> 26 == 15 and w & 0xFFFF == hi:  # lis rD,hi
        rd = (w >> 21) & 31
        for k in range(1, 12):
            w2 = struct.unpack_from('>I', data, off + 4 * k)[0]
            if w2 >> 26 == 14 and (w2 >> 16) & 31 == rd and w2 & 0xFFFF == lo:
                print(f"lis/addi ref at {0x82000000 + off:08X}"); break
