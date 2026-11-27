#!/usr/bin/env python3
# nlogx.py <natives-log.tsv> [filter...]: the full natives log (debug channel `nlog`, VICTORY_NATIVES=log) made readable:
# names from natives-names.txt, vectors decoded (a slot holding two plain floats followed by a slot whose low half is
# one), 32-bit values that are the joaat of a known word shown as `word` (words: natives-words.txt, a list of your own, if present).
# Filters (all must hold): from=<call> to=<call>  script=0x..  rva=+0x..[,+0x..]  max=<n: natives called at most n times in
# the file>  grep=<text>  byid (only by-ID calls)  first (only each native's first call)  ms=<from>-<to>
import sys,os,re,struct,collections
D=os.path.dirname(os.path.abspath(__file__))
def joaat(s):
    h=0
    for c in s.lower().encode('latin1','ignore'):
        h=(h+c)&0xffffffff; h=(h+(h<<10))&0xffffffff; h^=h>>6
    h=(h+(h<<3))&0xffffffff; h^=h>>11; return (h+(h<<15))&0xffffffff
def words():
    W={}
    for f in ('natives-words.txt',):
        p=os.path.join(D,f)
        if os.path.exists(p):
            for l in open(p,errors='ignore'):
                w=l.strip()
                if w and not w.startswith('#'): W.setdefault(joaat(w),w)
    return W
M={}
def names():
    N={}
    for l in open(os.path.join(D,'natives-names.txt')):
        w=l.split()
        if len(w)>=2 and not l.startswith('#') and w[1].startswith('0x'): N[int(w[1],16)]=w[0]
        elif len(w)>=2 and w[1].startswith('m+0x'): M['+'+w[1][2:]]=w[0]
    return N
def fl(v):
    f=struct.unpack('<f',struct.pack('<I',v&0xffffffff))[0]
    return f if f==f and (f==0 or 1e-3<abs(f)<1e5) else None
def slots(text):
    return [int(m,16) for m in re.findall(r'0x([0-9a-f]+)',text)]
def show(vals,W):
    out=[]; i=0
    while i<len(vals):
        v=vals[i]; lo,hi=v&0xffffffff,v>>32
        x,y=fl(lo),fl(hi)
        if hi and x is not None and y is not None and (abs(x)>1 or abs(y)>1) and i+1<len(vals) and fl(vals[i+1]) is not None and (lo>>20) not in (0,):
            out.append('v(%.2f,%.2f,%.2f)'%(x,y,fl(vals[i+1]))); i+=2; continue
        if hi==0 and lo in W: out.append('`%s`'%W[lo])
        elif (hi in (0xffffffff,0,1,0xd) or True) and lo in W and hi<0x10: out.append('%#x`%s`'%(v,W[lo]))
        elif hi==0 and x is not None and x!=0 and lo>0x10000: out.append('%g'%x)
        else: out.append('%#x'%v)
        i+=1
    return ' '.join(out)
if __name__=='__main__':
    flt=dict(a.split('=',1) if '=' in a else (a,'1') for a in sys.argv[2:])
    W=words(); N=names()
    rows=[l.rstrip('\n').split('\t') for l in open(sys.argv[1]) if not l.startswith('#')]
    cnt=collections.Counter(r[1] for r in rows); seen=set()
    rv=set(flt['rva'].split(',')) if 'rva' in flt else None
    ms=tuple(int(x) for x in flt['ms'].split('-')) if 'ms' in flt else None
    for r in rows:
        n=int(r[0])
        if 'from' in flt and n<int(flt['from']): continue
        if 'to' in flt and n>int(flt['to']): break
        if 'script' in flt and r[3]!=flt['script']: continue
        if rv and r[1] not in rv: continue
        if 'max' in flt and cnt[r[1]]>int(flt['max']): continue
        if 'byid' in flt and r[2]!='by-id': continue
        if ms and len(r)>7 and not ms[0]<=int(r[7])<=ms[1]: continue
        if 'first' in flt:
            if r[1] in seen: continue
            seen.add(r[1])
        name=N.get(int(r[2],16),'') if r[2].startswith('0x') else M.get(r[1],r[2])
        line=f"{r[0]} {r[7]+'ms ' if len(r)>7 else ''}{r[3]} {r[1]} {name or r[2][:10]} n={cnt[r[1]]} argc={r[4]} ({show(slots(r[5]),W)}) -> {show(slots(r[6]),W)}"
        if 'grep' in flt and flt['grep'] not in line: continue
        print(line)
