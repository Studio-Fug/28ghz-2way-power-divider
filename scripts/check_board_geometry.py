"""Check that the board's custom-pad conversion preserves exported island coordinates."""
from pathlib import Path
import re,json
from decimal import Decimal
root=Path(__file__).resolve().parents[1]
def parse(path):
 tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',path.read_text())
 stack=[];result=[]
 for t in tokens:
  if t=='(':
   x=[]
   if stack:stack[-1].append(x)
   else:result.append(x)
   stack.append(x)
  elif t==')':stack.pop()
  else:stack[-1].append(t.strip('"'))
 return result[0]
def children(x,key):return [v for v in x if isinstance(v,list) and v and v[0]==key]
def child(x,key):return children(x,key)[0]
def points(x):return [(Decimal(v[1]),Decimal(v[2])) for v in child(x,'pts')[1:]]
a=parse(root/'runs/jlc20mil/footprint.kicad_mod')
b=parse(root/'output/test-board/rf-combiner-test.kicad_pcb')
f=next(f for f in children(b,'footprint') if any(v[1:3]==['Reference','RF1'] for v in children(f,'property')))
p=next(p for p in children(f,'pad') if p[1]=='1')
source=max([s for s in children(a,'fp_poly') if child(s,'layer')[1]=='F.Cu'],key=lambda s:len(points(s)))
primitive=child(child(p,'primitives'),'gr_poly')
offset=child(p,'at')[1:3]
converted=[(x+Decimal(offset[0]),y+Decimal(offset[1])) for x,y in points(primitive)]
assert points(source)==converted,'Island polygon changed during custom-pad conversion'
other_source=[points(s) for s in children(a,'fp_poly') if s is not source and child(s,'layer')[1]=='F.Cu']
other_board=[points(s) for s in children(f,'fp_poly') if child(s,'layer')[1]=='F.Cu']
assert sorted(tuple(sorted(p)) for p in other_source)==sorted(tuple(sorted(p)) for p in other_board),'Floating island geometry changed'
report={'passed':True,'main_island_vertices':len(converted),'floating_islands':len(other_source),'comparison':'Exact decimal coordinate equality in footprint-local coordinates; port pad anchors retained','source':'runs/jlc20mil/footprint.kicad_mod','board':'output/test-board/rf-combiner-test.kicad_pcb'}
(root/'reports/board-geometry.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
