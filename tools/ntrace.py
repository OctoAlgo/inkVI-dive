#!/usr/bin/env python3
# ntrace.py <natives-trace.tsv> [filter...]: the run-time natives trace (debug channel `ndump`) joined with the static
# table natives-all.tsv if present (implementation callee, argument shape; not shipped) and natives-names.txt. Filters (all must hold):
#   str            only natives with a string argument in a sample
#   argc=N retc=N  counts
#   min=N max=N    call-count bounds
#   after=<mark substring> / before=<mark substring>   first call between marks (e.g. after='world 100')
#   script=0x..    a sample from that script
#   grep=<text>    text anywhere in the line
import sys,os,re
D=os.path.dirname(os.path.abspath(__file__))
stat={}
# natives-all.tsv (optional, not shipped: a table you can make from your own executable) adds callee and argument shape.
if os.path.exists(os.path.join(D,'natives-all.tsv')):
    for l in open(os.path.join(D,'natives-all.tsv')):
        if l.startswith('#'): continue
        f=l.rstrip('\n').split('\t'); stat[f[0]]=f
names={}
for l in open(os.path.join(D,'natives-names.txt')):
    w=l.split()
    if len(w)>=2 and not l.startswith('#') and w[1].startswith('0x'): names[int(w[1],16)]=w[0]
flt=dict(a.split('=',1) if '=' in a else (a,'1') for a in sys.argv[2:])
mark=''; seen_after='after' not in flt; out=[]
for l in open(sys.argv[1]):
    l=l.rstrip('\n')
    if l.startswith('# mark'):
        mark=l[7:]
        if 'after' in flt and flt['after'] in mark: seen_after=True
        if 'before' in flt and flt['before'] in mark: break
        if seen_after and 'quiet' not in flt: print('--', mark)
        continue
    if l.startswith('#') or not seen_after: continue
    rva,h,calls,argc,retc,first,samples=(l.split('\t')+[''])[:7]
    if 'str' in flt and '"' not in samples: continue
    if 'argc' in flt and argc!=flt['argc']: continue
    if 'retc' in flt and retc!=flt['retc']: continue
    if 'min' in flt and int(calls)<int(flt['min']): continue
    if 'max' in flt and int(calls)>int(flt['max']): continue
    if 'script' in flt and 'script='+flt['script']+' ' not in samples: continue
    s=stat.get(rva,['']*7)
    line=f"{rva} {h} {names.get(int(h,16),'')} n={calls} argc={argc} retc={retc} impl[{s[5]}] shape[{s[4]}] :: {samples}"
    if 'grep' in flt and flt['grep'] not in line: continue
    print(line[:int(flt.get('w','420'))])
