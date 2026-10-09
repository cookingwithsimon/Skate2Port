"""For each guest address, print its containing function and the strings that function references.
func_strings.py <bin> <skate2_init.cpp> <addr>..."""
import bisect, re, struct, sys
data = open(sys.argv[1], 'rb').read(); BASE = 0x82000000
funcs = sorted(int(m, 16) for m in re.findall(r'\{ 0x([0-9A-F]{8}), sub_', open(sys.argv[2]).read()))
def w(a): return struct.unpack_from('>I', data, a - BASE)[0]
def cstr(a):
    o = a - BASE
    if not 0 <= o < len(data): return None
    e = data.find(b'\0', o, o + 200)
    s = data[o:e] if e > o else b''
    return s.decode('latin1') if len(s) >= 4 and all(32 <= c < 127 for c in s) else None
for arg in sys.argv[3:]:
    a = int(arg, 16); i = bisect.bisect_right(funcs, a) - 1
    start, end = funcs[i], funcs[i + 1] if i + 1 < len(funcs) else a + 4
    regs, found = {}, []
    for pc in range(start, end, 4):
        x = w(pc); op = x >> 26; rd = (x >> 21) & 31; ra = (x >> 16) & 31; imm = x & 0xFFFF
        simm = imm - 0x10000 if imm & 0x8000 else imm
        if op == 15 and ra == 0: regs[rd] = (imm << 16) & 0xFFFFFFFF
        elif op in (14, 32, 34) and ra in regs:  # addi / lwz / lbz off a lis base
            s = cstr((regs[ra] + simm) & 0xFFFFFFFF)
            if s and s not in found: found.append(s)
    print(f"{a:08X} in sub_{start:08X}: {found[:6]}")
