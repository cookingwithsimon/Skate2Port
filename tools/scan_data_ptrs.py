"""List code addresses referenced from data sections that are not registered functions.
scan_data_ptrs.py <bin> <skate2_init.cpp>"""
import re, struct, sys
data = open(sys.argv[1], 'rb').read()
known = sorted(int(m, 16) for m in re.findall(r'\{ 0x([0-9A-F]{8}), sub_', open(sys.argv[2]).read()))
known_set = set(known)
CODE_LO, CODE_HI, BASE = 0x82310000, 0x82D09958, 0x82000000
import bisect
cands = {}
for off in range(0, len(data) - 3, 4):
    a = BASE + off
    if CODE_LO <= a < CODE_HI:
        continue  # skip code (jump tables live there and are handled separately)
    v = struct.unpack_from('>I', data, off)[0]
    if CODE_LO <= v < CODE_HI and v % 4 == 0 and v not in known_set:
        cands.setdefault(v, []).append(a)
def ins(v): return struct.unpack_from('>I', data, v - BASE)[0]
for v in sorted(cands):
    i = bisect.bisect_right(known, v) - 1
    parent = known[i] if i >= 0 else 0
    prev = ins(v - 4)
    # previous instruction is blr / b / padding => looks like a real function start
    boundary = prev in (0x4E800020, 0x4E800420, 0) or prev >> 26 == 18
    print(f"{v:08X} parent={parent:08X} refs={len(cands[v])} first_ref={cands[v][0]:08X} first_ins={ins(v):08X} {'START' if boundary else 'interior'}")
