"""Build the RF test fixture from YAPNR's exported copper, using headless pcbnew."""
from pathlib import Path
import json
import math
import sys
import re
import pcbnew as k

OUT = Path('output/test-board')
OUT.mkdir(parents=True, exist_ok=True)
MM = k.FromMM
V = lambda x, y: k.VECTOR2I(MM(x), MM(y))
board = k.BOARD()
board.SetCopperLayerCount(2)
ds = board.GetDesignSettings()
ds.SetBoardThickness(MM(.65))
ds.m_MinClearance = MM(.15)
ds.m_TrackMinWidth = MM(.15)
ds.m_CopperEdgeClearance = MM(.15)
ds.m_SolderMaskExpansion = MM(.025)
ds.m_SolderMaskMinWidth = MM(.10)
ds.m_MinThroughDrill = MM(.30)
ds.m_ViasMinSize = MM(.8)
ds.m_ViasMinAnnularWidth = MM(.25)
ds.m_HoleClearance = MM(.25)
ds.m_SilkClearance = MM(.15)
ds.m_MinSilkTextHeight = MM(.8)
ds.m_MinSilkTextThickness = MM(.12)

def net(name):
    n = k.NETINFO_ITEM(board, name)
    board.Add(n)
    return n

gnd = net('GND')
# The Wilkinson copper connects all three ports and both resistor terminals at DC.
# Keep the port numbers as microwave identifiers; use one DC net for that island.
signal=net('RF')
rf=[signal,signal,signal]
ra=rb=signal

def segment(a, b, width, n, layer=k.F_Cu):
    s = k.PCB_TRACK(board)
    s.SetStart(V(*a)); s.SetEnd(V(*b)); s.SetWidth(MM(width))
    s.SetLayer(layer); s.SetNet(n); board.Add(s)

def shape_line(a, b, layer=k.Edge_Cuts, width=.05, parent=board):
    s = k.PCB_SHAPE(parent)
    s.SetShape(k.SHAPE_T_SEGMENT); s.SetStart(V(*a)); s.SetEnd(V(*b))
    s.SetWidth(MM(width)); s.SetLayer(layer)
    parent.Add(s)

def label(text, x, y, size=1.0):
    t = k.PCB_TEXT(board)
    t.SetText(text); t.SetPosition(V(x,y)); t.SetTextSize(V(size,size))
    t.SetTextThickness(MM(.15)); t.SetLayer(k.F_SilkS)
    board.Add(t)

def via(x,y):
    v = k.PCB_VIA(board)
    v.SetPosition(V(x,y)); v.SetWidth(MM(.8)); v.SetDrill(MM(.30))
    v.SetViaType(k.VIATYPE_THROUGH); v.SetLayerPair(k.F_Cu,k.B_Cu)
    v.SetNet(gnd); board.Add(v)

def pad(fp, num, x,y,sx,sy,n=None, drill=None):
    p=k.PAD(fp); p.SetNumber(str(num)); p.SetPosition(V(x,y))
    p.SetSize(V(sx,sy))
    if drill:
        p.SetAttribute(k.PAD_ATTRIB_NPTH); p.SetShape(k.PAD_SHAPE_CIRCLE)
        p.SetDrillSize(V(drill,drill)); p.SetLayerSet(k.PAD.UnplatedHoleMask())
    else:
        p.SetAttribute(k.PAD_ATTRIB_SMD); p.SetShape(k.PAD_SHAPE_RECT)
        layers=k.LSET(); layers.AddLayer(k.F_Cu); layers.AddLayer(k.F_Mask)
        p.SetLayerSet(layers)
        if n: p.SetNet(n)
    fp.Add(p)
    return p

def connector(ref,x,y,right,n):
    """1092-03A-6 standard .500 block; .375 hole spacing / .110 setback.

    Mechanical dimensions: Southwest Microwave 91Y60926 rev A and 2024 brochure.
    The planar transition is a test launch, not a manufacturer-validated EM launch.
    """
    fp=k.FOOTPRINT(board)
    fp.SetFPID(k.LIB_ID('RF_Test','SWM_1092-03A-6_'+('Right' if right else 'Left')))
    fp.SetReference(ref); fp.SetValue('1092-03A-6')
    fp.SetPosition(V(x,y))
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    fp.SetAttributes(k.FP_SMD | k.FP_EXCLUDE_FROM_POS_FILES)
    inward=-1 if right else 1
    # Signal land starts at the milled board edge; the .010 inch pin is centered on it.
    pad(fp,1,x+inward*.6,y,.8,.45,n)
    # Two mask-open ground rails, with a wide gap from the microstrip/taper.
    for i,sign in enumerate((-1,1),2):
        pad(fp,i,x+inward*.85,y+sign*3.9,1.3,4.5,gnd)
    for sign in (-1,1):
        pad(fp,'',x+inward*2.79,y+sign*4.765,2.06,2.06,drill=2.06)
    # Connector body outline on F.Fab (it extends beyond the board).
    corners=[(x-inward*18.94,y-6.35),(x+inward*4.24,y-6.35),
             (x+inward*4.24,y+6.35),(x-inward*18.94,y+6.35)]
    for a,b in zip(corners,corners[1:]+corners[:1]):
        shape_line(a,b,k.F_Fab,.1,fp)
    board.Add(fp)
    # Low-inductance via connections within the exposed ground rails.
    for sign in (-1,1):
        for inset in (.65,1.30):
            for dy in (2.25,3.10,5.65):
                via(x+inward*inset,y+sign*dy)
    lib=OUT/'RF_Test.pretty'
    lib.mkdir(exist_ok=True)
    k.PCB_IO_MGR.FindPlugin(k.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(lib.resolve()),fp)
    return fp

W,H=40.,36.
for a,b in zip([(0,0),(W,0),(W,H),(0,H)],[(W,0),(W,H),(0,H),(0,0)]):
    shape_line(a,b)

fp_path=Path(sys.argv[1] if len(sys.argv)>1 else 'runs/jlc20mil/footprint.kicad_mod')
if not fp_path.exists():
    raise FileNotFoundError('The optimized footprint must exist before the fixture is built.')
fp=k.FootprintLoad(str(fp_path.parent.resolve()),fp_path.stem)
if fp is None: raise RuntimeError('KiCad could not load the YAPNR footprint')
fp.SetReference('RF1'); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
fp.SetPosition(V(20,18)); board.Add(fp)
group_text=re.search(r'\(net_tie_pad_groups\s+([^)]*)\)',fp_path.read_text()).group(1)
groups=[set(int(n.strip()) for n in g.split(',')) for g in re.findall(r'"([^"]+)"',group_text)]
if not any({1,2,3,4,5}.issubset(group) for group in groups):
    raise ValueError('The selected copper does not DC-connect all Wilkinson terminals.')
# KiCad's footprint copper polygons need an explicit net when their net-tie pads
# share one net. Floating parasitic islands remain netless.
copper=[s for s in fp.GraphicalItems() if isinstance(s,k.PCB_SHAPE) and s.GetLayer()==k.F_Cu]
largest=max(copper,key=lambda s:abs(s.GetPolyShape().Area()))
# Preserve the exact exported island as a custom-pad primitive: unlike a
# footprint graphic, this copper participates in KiCad DC connectivity.
anchor=next(p for p in fp.Pads() if p.GetNumber()=='1')
poly=k.SHAPE_POLY_SET(largest.GetPolyShape())
poly.Move(-anchor.GetPosition())
anchor.SetShape(k.PAD_SHAPE_CUSTOM)
anchor.SetAnchorPadShape(k.F_Cu,k.PAD_SHAPE_RECT)
anchor.AddPrimitivePoly(k.F_Cu,poly,0,True)
fp.Remove(largest)
padnets={1:rf[0],2:rf[1],3:rf[2],4:ra,5:rb}
ports={}
for p in fp.Pads():
    num=int(p.GetNumber()); p.SetNet(padnets[num])
    if num<=3:
        ports[num]=(k.ToMM(p.GetPosition().x),k.ToMM(p.GetPosition().y),k.ToMM(p.GetSize().y))

connector('J1',0,18,False,rf[0])
connector('J2',W,10,True,rf[1])
connector('J3',W,26,True,rf[2])

def taper(points,n,num):
    f=k.FOOTPRINT(board); f.SetReference('TP'+str(num))
    f.SetAttributes(k.FP_SMD | k.FP_EXCLUDE_FROM_POS_FILES | k.FP_EXCLUDE_FROM_BOM)
    f.Reference().SetVisible(False); f.Value().SetVisible(False)
    p=k.PAD(f); p.SetNumber('1'); p.SetAttribute(k.PAD_ATTRIB_SMD)
    p.SetShape(k.PAD_SHAPE_CUSTOM); p.SetPosition(V(*points[0])); p.SetSize(V(.15,.15))
    l=k.LSET(); l.AddLayer(k.F_Cu); l.AddLayer(k.F_Mask); p.SetLayerSet(l); p.SetNet(n)
    poly=k.SHAPE_POLY_SET(); poly.NewOutline()
    ox,oy=points[0]
    for x,y in points: poly.Append(MM(x-ox),MM(y-oy))
    p.AddPrimitivePoly(k.F_Cu,poly,0,True); f.Add(p); board.Add(f)

# Smooth board-edge pin-to-microstrip transitions, unchanged for all three ports.
for num,edge,y,inward in [(1,0,18,1),(2,40,10,-1),(3,40,26,-1)]:
    width=ports[num][2]
    # Pin land (.45 mm) to calibrated microstrip width over 2 mm.
    taper([(edge+inward*.8,y-.225),(edge+inward*2.8,y-width/2),
           (edge+inward*2.8,y+width/2),(edge+inward*.8,y+.225)],rf[num-1],num)
    x0,y0,_=ports[num]
    if num==1:
        segment((2.8,18),(x0,y0),width,rf[0])
    else:
        # Equal length mirrored output routes; bends start beyond the simulated keepout.
        start=(x0,y0); elbow1=(28,y0); elbow2=(28+abs(y-y0),y)
        for a,b in zip([start,elbow1,elbow2], [elbow1,elbow2,(37.2,y)]):
            segment(a,b,width,rf[num-1])

# Entire RF copper and feeds are mask-open: no unmodelled dielectric loading.
mask=k.PCB_SHAPE(board); mask.SetShape(k.SHAPE_T_RECT)
mask.SetStart(V(16.9,14.9)); mask.SetEnd(V(23.1,21.1)); mask.SetFilled(True)
mask.SetWidth(0); mask.SetLayer(k.F_Mask); board.Add(mask)
for track in list(board.GetTracks()):
    if isinstance(track,k.PCB_VIA): continue
    opening=k.PCB_SHAPE(board); opening.SetShape(k.SHAPE_T_SEGMENT)
    opening.SetStart(track.GetStart()); opening.SetEnd(track.GetEnd())
    opening.SetWidth(track.GetWidth()+MM(.05)); opening.SetLayer(k.F_Mask)
    board.Add(opening)

# Continuous ground directly beneath the RF layer, including beneath the combiner.
z=k.ZONE(board); z.SetLayer(k.B_Cu); z.SetNet(gnd)
z.SetLocalClearance(MM(.25)); z.SetPadConnection(k.ZONE_CONNECTION_FULL)
z.SetMinThickness(MM(.15)); poly=z.Outline(); poly.NewOutline()
for x,y in [(0,0),(W,0),(W,H),(0,H)]: poly.Append(MM(x),MM(y))
board.Add(z)

label('RF COMBINER / 24-32 GHz',20,2.0,1.15)
label('RO4350B  |  0.51 mm CORE',20,33.2,1.0)
label('J1 / SUM',8,18-3.2,.9)
label('J2 / IN A',32,6.5,.9)
label('J3 / IN B',32,29.5,.9)
label('R1 100R / CH02016',20,12.8,.8)
label('RF-28 REV A',11,30.6,.85)

board.BuildConnectivity()
k.ZONE_FILLER(board).Fill(board.Zones())
path=OUT/'rf-combiner-test.kicad_pcb'
k.SaveBoard(str(path),board)
text=path.read_text()
# Explicit fabrication stackup; finished thickness includes plating and finishes.
stack='''(stackup
  (layer "F.Cu" (type "copper") (thickness 0.035))
  (layer "dielectric 1" (type "core") (thickness 0.51) (material "RO4350B")
    (epsilon_r 3.66) (loss_tangent 0.0037))
  (layer "B.Cu" (type "copper") (thickness 0.035))
  (copper_finish "ENIG") (dielectric_constraints yes))'''
idx=text.index('(setup')+len('(setup')
text=text[:idx]+'\n'+stack+text[idx:]
path.write_text(text)

project={'board':{'design_settings':{'rules':{
    'min_clearance':.15,'min_track_width':.15,'min_via_diameter':.8,
    'min_through_hole_diameter':.30,'min_hole_clearance':.25,
    'min_copper_edge_clearance':.15,'min_silk_clearance':.15,
    'min_silk_text_height':.8,'min_silk_text_thickness':.12,
    'min_hole_to_hole':.25}}},
    'net_settings':{'classes':[{'name':'Default','clearance':.15,'track_width':1.2,
                               'via_diameter':.8,'via_drill':.30}]}}
(OUT/'rf-combiner-test.kicad_pro').write_text(json.dumps(project,indent=2)+'\n')
(OUT/'fp-lib-table').write_text('(fp_lib_table (version 7)\n'
    '  (lib (name "RF_Test")(type "KiCad")(uri "${KIPRJMOD}/RF_Test.pretty")(options "")(descr "Verified mechanical launch footprints"))\n)\n')
(OUT/'BOM.csv').write_text('Reference,Qty,Value,Manufacturer,Part,Assembly\n'
 'J1 J2 J3,3,2.92mm 40GHz edge launch,Southwest Microwave,1092-03A-6,Manual clamp installation\n'
 'R1,1,100 ohm 70GHz thin-film resistor,Vishay Sfernice,CH02016-100RGFTF,Manual active face down; pads 4 and 5 of RF1\n')
(OUT/'geometry.json').write_text(json.dumps({'board_mm':[W,H],'ports':ports,
    'connector':'1092-03A-6','mounting_holes':{'diameter_mm':2.06,'setback_mm':2.79,'spacing_mm':9.53}},indent=2)+'\n')
print(path)
