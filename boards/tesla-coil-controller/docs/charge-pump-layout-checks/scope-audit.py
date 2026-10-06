import json,sys,hashlib
from pathlib import Path
from collections import Counter
sys.path.insert(0,'tools/hardware')
from tesla_schematic_layout import parse,child,children,walk
root=Path('.');base=Path('/tmp/tesla-testpoint-layout/before');rel=Path('boards/tesla-coil-controller');out=rel/'docs/charge-pump-layout-checks'
def get(p):return parse(p.read_text())
a=get(base/rel/'controller.kicad_sch');b=get(rel/'controller.kicad_sch')
def normalize(n):
 if not isinstance(n,list):return n
 if n and n[0]=='uuid':return None
 q=[normalize(x) for x in n];q=[x for x in q if x is not None]
 if q and q[0]=='property' and q[1]=='Reference' and q[2].startswith('#PWR'):q[2]='#PWR'
 if q and q[0]=='reference' and q[1].startswith('#PWR'):q[1]='#PWR'
 return q
def enc(n):return json.dumps(normalize(n),sort_keys=True)
def ref(n):return next(p[2] for p in children(n,'property') if p[1]=='Reference')
def symdict(n):return {ref(s):s for s in children(n,'symbol') if not ref(s).startswith('#PWR')}
sa,sb=symdict(a),symdict(b)
assert sa.keys()==sb.keys()
changed=[r for r in sa if enc(sa[r])!=enc(sb[r])]
allowed={'U44','C420','C421','C422','C423','R421','#FLG004'}
assert set(changed)<=allowed,changed
assert enc(child(a,'lib_symbols'))==enc(child(b,'lib_symbols'))
la=json.loads((base/rel/'docs/schematic-layout.json').read_text());lb=json.loads((rel/'docs/schematic-layout.json').read_text())
before=next(x for x in la if x['id']==12);after=next(x for x in lb if x['id']==12)
assert [x for x in la if x['id']!=12]==[x for x in lb if x['id']!=12]
def outside(n,box):
 pts=[list(map(float,p[1:3])) for p in walk(n) if p[0] in ('xy','start','end')]
 at=child(n,'at')
 if at:pt=list(map(float,at[1:3]))
 elif pts:pt=[sum(p[k] for p in pts)/len(pts) for k in (0,1)]
 else:return False
 x,y=box['position'];w,h=box['size']
 return not (x-.01<=pt[0]<=x+w+.01 and y-.01<=pt[1]<=y+h+.01)
geom={'symbol','wire','junction','no_connect','global_label','label','text','rectangle','polyline','bus','bus_entry','hierarchical_label','text_box'}
def outside_items(doc,box):return Counter(enc(n) for n in doc if isinstance(n,list) and n and n[0] in geom and outside(n,box))
oa,ob=outside_items(a,before),outside_items(b,after)
assert oa==ob,(list((oa-ob).elements())[:2],list((ob-oa).elements())[:2])
# Native sync verifies net membership; this read-only geometric trace verifies
# the flag reaches the tested filter node through actual wires, without labels.
libs={n[1]:n for n in children(child(b,'lib_symbols'),'symbol')}
def pin(r,num):
 s=sb[r];at=child(s,'at');x,y=map(float,at[1:3]);p=next(n for n in walk(libs[child(s,'lib_id')[1]]) if n[0]=='pin' and child(n,'number')[1]==str(num));u,v=map(float,child(p,'at')[1:3]);return round(x+u,4),round(y-v,4)
segments=[tuple(tuple(map(float,p[1:3])) for p in children(child(w,'pts'),'xy')) for w in children(b,'wire')]
flag=pin('#FLG004',1);targets={'R421.2':pin('R421',2),'C423.1':pin('C423',1)}
def on(p,seg):
 (x,y),(u,v)=seg;return abs((p[0]-x)*(v-y)-(p[1]-y)*(u-x))<1e-5 and min(x,u)-1e-5<=p[0]<=max(x,u)+1e-5 and min(y,v)-1e-5<=p[1]<=max(y,v)+1e-5
reached={flag};chosen=[]
while True:
 new=[s for s in segments if s not in chosen and any(on(p,s) for p in reached)]
 if not new:break
 for s in new:
  chosen.append(s);reached.update(s);reached.update(p for p in targets.values() if on(p,s))
assert all(p in reached for p in targets.values()),(flag,targets,reached)
assert any(flag in s for s in segments),'flag is not at wire endpoint'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
hashes={}
for f in ['controller.kicad_pcb','controller.kicad_pro','docs/circuit.json','Tesla.kicad_sym']:
 beforehash=sha(base/rel/f);afterhash=sha(rel/f);assert beforehash==afterhash,f;hashes[f]=afterhash
report=dict(changed_symbols=changed,embedded_library_unchanged=True,other_blocks_unchanged=True,outside_geometry_items=sum(oa.values()),outside_geometry_unchanged=True,before_size_mm=before['size'],after_size_mm=after['size'],width_reduction_percent=round(100*(1-after['size'][0]/before['size'][0]),2),height_reduction_percent=round(100*(1-after['size'][1]/before['size'][1]),2),area_reduction_percent=round(100*(1-after['size'][0]*after['size'][1]/before['size'][0]/before['size'][1]),2),flag_wire_endpoint_mm=flag,connected_by_wire=targets,unchanged_file_sha256=hashes)
(out/'scope-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
