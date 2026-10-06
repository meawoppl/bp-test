"""Presentation-only landscape packing of wired Tesla schematic blocks.

Translate whole blocks on the connection grid; never scale symbols or wires.
Content-derived bounds include visible fields, labels and library geometry.
"""
import re,json,math
from pathlib import Path
TOKEN=re.compile(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+')
def parse(s):
 stack=[];root=None
 for t in TOKEN.findall(s):
  if t=='(':
   n=[]
   if stack:stack[-1].append(n)
   stack.append(n)
  elif t==')':root=stack.pop()
  else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
 return root
def children(n,k):return [a for a in n if isinstance(a,list) and a and a[0]==k]
def child(n,k):return next(iter(children(n,k)),None)
def walk(n):
 if isinstance(n,list):
  yield n
  for a in n:yield from walk(a)
def bounds(s,symbols):
 n=parse(s);pts=[]
 if n[0]=='symbol':
  at=child(n,'at');x,y=map(float,at[1:3]);lib=child(n,'lib_id')[1].split(':',1)[1]
  for a in walk(parse(symbols[lib])):
   if a and a[0] in ['xy','start','end','at'] and len(a)>2:
    try:pts.append((x+float(a[1]),y-float(a[2])))
    except ValueError:pass
  fields=children(n,'property')
 else:
  for a in walk(n):
   if a and a[0] in ['xy','start','end','at'] and len(a)>2:
    pts.append(tuple(map(float,a[1:3])))
  fields=[n] if n[0] in ['text','global_label','label'] else []
 for f in fields:
  if child(f,'hide'):continue
  at=child(f,'at');eff=child(f,'effects')
  if not at or not eff:continue
  size=child(child(eff,'font'),'size');sz=float(size[1]);txt=f[2] if f[0]=='property' else f[1];w=len(txt)*sz*.68+2;xx,yy=map(float,at[1:3]);just=child(eff,'justify')
  if just and just[1]=='left':lo,hi=xx,xx+w
  elif just and just[1]=='right':lo,hi=xx-w,xx
  else:lo,hi=xx-w/2,xx+w/2
  pts.extend([(lo,yy-sz),(hi,yy+sz)])
 return [min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)]
def translate(s,dx,dy):
 return re.sub(r'\((at|xy|start|end) (-?[\d.]+) (-?[\d.]+)',lambda m:f'({m[1]} {float(m[2])+dx:.4f} {float(m[3])+dy:.4f}',s)
TITLES=['DAUGHTERBOARD / FPGA + ESP32','ADC / AD7606C-16','ANALOG INPUTS / ADC RC FILTERS','ADC / LOCAL BYPASS + REFERENCE','ANALOG + LOGIC SUPPLIES','USB-C / PROGRAMMING ONLY','DESIGN NOTES','24 V TO 12 V / DRIVER BIAS','24 V TO 5 V / LOGIC','BATTERY INPUTS / SERIES LINK + RESERVOIR','CST 1 / INPUT + PRECISION RECTIFIER','CST 1 / PHASE COMPARATOR + REFERENCE','SHARED -5 V / CHARGE PUMP','CST 1 / PHASE REFERENCE','CST 1 / LOCAL BYPASS','CST 2 / INPUT + PRECISION RECTIFIER','CST 2 / PHASE COMPARATOR + REFERENCE','CST 2 / PHASE REFERENCE','CST 2 / LOCAL BYPASS','GDT 1 / FPGA COMMAND DAMPING','GDT 2 / FPGA COMMAND DAMPING','GDT 1 / FULL BRIDGE + GATE BIAS','GDT 2 / FULL BRIDGE + GATE BIAS','AUX 1 / UNITY BUFFER','AUX 2 / UNITY BUFFER','AUX 3 / UNITY BUFFER','AUX 4 / UNITY BUFFER','LOCAL POWER + BRIDGE LEG INDICATORS','MOUNTING']
def reflow(items,symbols,uid,out):
 # The two former reference blocks now belong to their phase comparators.
 # Preserve all other block IDs, positions and UUIDs when retiring those boxes.
 block_ids=[j for j in range(28) if j not in (13,17)]
 boxes={};skip=set()
 for i,s in enumerate(items):
  if s.startswith('(rectangle'):
   n=parse(s);a=child(n,'start');z=child(n,'end');boxes[block_ids[len(boxes)]]=[*map(float,a[1:3]),*map(float,z[1:3])];skip.update([i,i+1])
 assert len(boxes)==len(block_ids)
 groups={j:[] for j in [*block_ids,28]}
 for i,s in enumerate(items):
  if i in skip:continue
  n=parse(s)
  if n[0]=='symbol' and any(f[1]=='Reference' and f[2] in ['H1','H2','H3','H4','H5'] for f in children(n,'property')):j=28
  else:
   a=child(n,'at')
   if a:x,y=map(float,a[1:3])
   else:
    ps=[a for a in walk(n) if a and a[0]=='xy'];x=sum(float(a[1]) for a in ps)/len(ps);y=sum(float(a[2]) for a in ps)/len(ps)
   def dist(b):return max(b[0]-x,0,x-b[2])**2+max(b[1]-y,0,y-b[3])**2
   j=min(boxes,key=lambda j:dist(boxes[j]))
  groups[j].append(s)
 # Pull trailing explanatory notes up to the actual circuit, retaining in-circuit
 # annotations (e.g. capacitor-bank headings) in their original positions.
 for ss in groups.values():
  bottom=max(bounds(s,symbols)[3] for s in ss if not s.startswith('(text '))
  trailing=[]
  for i,s in enumerate(ss):
   if s.startswith('(text '):
    yy=float(child(parse(s),'at')[2])
    if yy>bottom+5.08:trailing.append((yy,i))
  for k,(yy,i) in enumerate(sorted(trailing)):
   dy=round((bottom+7.62+k*5.08-yy)/1.27)*1.27
   ss[i]=translate(ss[i],0,dy)
 sizes={};bb={}
 for j,ss in groups.items():
  bs=[bounds(s,symbols) for s in ss];b=[min(a[0] for a in bs),min(a[1] for a in bs),max(a[2] for a in bs),max(a[3] for a in bs)];bb[j]=b
  sizes[j]=[math.ceil((b[2]-b[0]+12)/1.27)*1.27,math.ceil((b[3]-b[1]+19)/1.27)*1.27]
 # Repeated channels share box edges while retaining their native symbol scale.
 for ids in ((7,8),(23,24,25,26),(19,20,21,22)):
  width=max(sizes[j][0] for j in ids)
  for j in ids:sizes[j][0]=width
 # Pack related sections from their current measured sizes. Fixed coordinates
 # become stale whenever an individual circuit is shortened or expanded.
 layout_path=Path(__file__).with_name('tesla_schematic_layout.json')
 layout=json.loads(layout_path.read_text());gap=layout['gap'];margin=layout['margin']
 positions={}
 def pack(node,x,y):
  if isinstance(node,int):
   assert node not in positions,('Repeated schematic block',node)
   positions[node]=(x,y)
   return sizes[node]
  axis,entries=next(iter(node.items()))
  assert axis in ('row','column') and entries
  w=h=0
  for entry in entries:
   ew,eh=pack(entry,x+w if axis=='row' else x,y+h if axis=='column' else y)
   if axis=='row':w+=ew+gap;h=max(h,eh)
   else:w=max(w,ew);h+=eh+gap
  return (w-gap,h) if axis=='row' else (w,h-gap)
 pack(layout['layout'],margin,margin)
 assert set(positions)==set(groups),'Every schematic block must be placed once'
 for i in groups:
  ax,ay=positions[i];aw,ah=sizes[i]
  for j in groups:
   if j>=i:continue
   bx,by=positions[j];bw,bh=sizes[j]
   assert min(ax+aw,bx+bw)<=max(ax,bx) or min(ay+ah,by+bh)<=max(ay,by),('Overlapping schematic blocks',i,j)
 result=[];audit=[]
 for j,ss in groups.items():
  x,y=positions[j];w,h=sizes[j];dx=round((x+6-bb[j][0])/1.27)*1.27;dy=round((y+13-bb[j][1])/1.27)*1.27
  result.extend(translate(s,dx,dy) for s in ss)
  result.append(f'(rectangle (start {x} {y}) (end {x+w} {y+h}) (stroke (width 0.254) (type default)) (fill (type none)) (uuid "{uid("landscape-box-"+str(j))}"))')
  result.append(f'(text {json.dumps(TITLES[j])} (at {x+5.08} {y+5.08} 0) (effects (font (size 2 2)) (justify left)) (uuid "{uid("landscape-title-"+str(j))}"))')
  audit.append(dict(id=j,title=TITLES[j],old_bounds=boxes[j] if j<28 else None,content_bounds=bb[j],size=sizes[j],position=positions[j],items=len(ss)))
 (out/'schematic-layout.json').write_text(json.dumps(audit,indent=2)+'\n')
 width=max(positions[j][0]+sizes[j][0] for j in groups)+margin;height=max(positions[j][1]+sizes[j][1] for j in groups)+margin
 return result,(width,height)
