"""List code addresses built with lis/addi in code that are not registered functions
and look like function starts. scan_code_ptrs.py <bin> <skate2_init.cpp>"""
import re, struct, sys
data = open(sys.argv[1], 'rb').read(); BASE = 0x82000000
CODE_LO, CODE_HI = 0x82310000, 0x82D09958
known = set(int(m, 16) for m in re.findall(r'\{ 0x([0-9A-F]{8}), sub_', open(sys.argv[2]).read()))
def w(a): return struct.unpack_from('>I', data, a - BASE)[0]
found = {}
for pc in range(CODE_LO, CODE_HI - 4, 4):
    x = w(pc)
    if x >> 26 != 15 or (x >> 16) & 31: continue  # lis rD,imm
    rd = (x >> 21) & 31; hi = (x & 0xFFFF) << 16
    for k in range(1, 16):
        y = w(pc + 4 * k)
        if y >> 26 == 14 and (y >> 16) & 31 == rd:  # addi rX,rD,imm
            lo = y & 0xFFFF; lo -= 0x10000 if lo & 0x8000 else 0
            t = (hi + lo) & 0xFFFFFFFF
            if CODE_LO <= t < CODE_HI and t % 4 == 0 and t not in known:
                found.setdefault(t, pc)
            break
        if (y >> 21) & 31 == rd and y >> 26 not in (36, 37, 38, 44, 45, 52, 54): break  # rD overwritten
for t in sorted(found):
    first, prev = w(t), w(t - 4)
    if first >> 24 == 0x82 or first >> 26 == 0: continue  # jump table / data, not code
    boundary = prev in (0x4E800020, 0x4E800420, 0, 0x48000004) or prev >> 26 == 18
    if boundary: print(f"{t:08X} ref={found[t]:08X} first_ins={first:08X}")
