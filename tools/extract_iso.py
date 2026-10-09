"""Extract an Xbox 360 game ISO (XDVDFS).
Usage: extract_iso.py <iso> list | extract_iso.py <iso> extract-all <out_dir>"""
import sys, struct, os
iso = sys.argv[1]; mode = sys.argv[2] if len(sys.argv)>2 else 'list'; out = sys.argv[3] if len(sys.argv)>3 else None
f = open(iso,'rb')
base=None
for off in (0, 0x2080000, 0xFD90000, 0x18300000):
    f.seek(off+0x10000)
    if f.read(20)==b'MICROSOFT*XBOX*MEDIA': base=off;break
print('partition base', hex(base))
f.seek(base+0x10000+20); root_sec, root_size = struct.unpack('<II', f.read(8))
entries=[]
def walk(sec, size, path):
    f.seek(base+sec*2048); data=f.read(size)
    stack=[0]; seen=set()
    while stack:
        o=stack.pop()
        if o in seen or o*4+14>len(data): continue
        seen.add(o); p=o*4
        l,r,s,sz,attr,nl=struct.unpack('<HHIIBB',data[p:p+14])
        if l==0xFFFF: continue
        name=data[p+14:p+14+nl].decode('latin1')
        if l: stack.append(l)
        if r: stack.append(r)
        full=path+'/'+name
        if attr&0x10:
            if sz: walk(s,sz,full)
        else: entries.append((full,s,sz))
walk(root_sec, root_size, '')
if mode=='list':
    tot=0
    for e in sorted(entries): print(e[2], e[0]); tot+=e[2]
    print('files', len(entries), 'bytes', tot)
else:
    for full,s,sz in entries:
        if full.lower()==mode.lower():
            f.seek(base+s*2048); open(out,'wb').write(f.read(sz)); print('wrote',out,sz)
if mode=='extract-all':
    import os
    for full,s,sz in entries:
        dst=os.path.join(out, *full.strip('/').split('/'))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst) and os.path.getsize(dst)==sz: continue
        f.seek(base+s*2048); left=sz
        with open(dst,'wb') as o:
            while left:
                b=f.read(min(left, 64<<20)); o.write(b); left-=len(b)
    print('extracted', len(entries), 'files to', out)
