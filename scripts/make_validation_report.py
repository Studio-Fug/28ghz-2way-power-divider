"""Generate one-requirement-per-case evidence from committed simulation artifacts."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
run=ROOT/'runs/jlc20mil'
out=ROOT/'reports'; out.mkdir(exist_ok=True)
comparison=json.loads((run/'comparison.json').read_text())
checks=[
 ('REQ-1','Return loss >=15 dB at each port over 24-32 GHz','return_loss_min_db_per_port',lambda v:min(v)>=15,'minimum per-port return loss'),
 ('REQ-2','Isolation >=14 dB over 24-32 GHz','isolation_min_db',lambda v:v>=14,'minimum isolation'),
 ('REQ-3','Excess insertion loss <=0.7 dB in both directions over 24-32 GHz','excess_loss_max_db',lambda v:v<=.7,'maximum excess loss'),
 ('REQ-4','Amplitude imbalance <=0.5 dB over 24-32 GHz','amplitude_imbalance_max_db',lambda v:v<=.5,'maximum imbalance'),
 ('REQ-5','Phase imbalance <=5 degrees over 24-32 GHz','phase_imbalance_max_deg',lambda v:v<=5,'maximum phase imbalance'),
 ('REQ-6','Equal-phase coherent combining loss <=0.7 dB','coherent_combining_loss_max_db',lambda v:v<=.7,'maximum coherent loss'),
 ('REQ-7','Scattering matrix is passive within 0.001 numerical tolerance','passivity_margin_min',lambda v:v>=-.001,'minimum eigenvalue of I-S†S'),
]
model={'user_needs':[
 {'id':'UN-1','title':'Comparable small-signal two-way 24-32 GHz combiner'},
 {'id':'UN-2','title':'JLC-compatible test coupon using 0.51 mm core and 2.92 mm launches'},
 {'id':'UN-3','title':'Traceable design with reproducible simulation evidence'}],
 'requirements':[], 'test_methods':[
 {'id':'TM-1','title':'Exported-footprint native FDTD on three grids','level':'simulation','description':'81 frequencies from 24 to 32 GHz; 50 ohm renormalization; inspect reports/validation.md for limitations.'},
 {'id':'TM-2','title':'KiCad native DRC and geometry inspection','level':'inspection'},
 {'id':'TM-3','title':'Calibrated three-port VNA measurement','level':'hil'},
 {'id':'TM-4','title':'Controlled-power thermal qualification','level':'hil'},
 {'id':'TM-5','title':'Complete assembly EM/co-simulation at coaxial connector planes','level':'simulation'},
 {'id':'TM-6','title':'Assembly model coverage and provenance inspection','level':'inspection'}]}
suites=ET.Element('testsuites')
def case(suite,name,req,level,passed,detail):
 c=ET.SubElement(suite,'testcase',name=name,classname='rf_validation')
 props=ET.SubElement(c,'properties')
 for k,v in [('requirement',req),('level',level),('artifact.footprint_sha256',hashlib.sha256((run/'footprint.kicad_mod').read_bytes()).hexdigest())]:
  ET.SubElement(props,'property',name=k,value=v)
 if not passed: ET.SubElement(c,'failure',message=detail).text=detail
 ET.SubElement(c,'system-out').text=detail
for req,title,key,predicate,label in checks:
 model['requirements'].append({'id':req,'title':'DUT-plane: '+title,'satisfies':['UN-1' if req in ['REQ-1','REQ-2','REQ-3','REQ-4','REQ-5','REQ-6'] else 'UN-3'],'method':'TM-1','description':'Simulation-only acceptance. Physical equivalence requires REQ-11.'})
for grid in ['coarse','fine','finer']:
 s=ET.SubElement(suites,'testsuite',name=grid)
 if grid not in comparison['grids']:
  for req,title,key,predicate,label in checks:
   c=ET.SubElement(s,'testcase',name=grid+'_'+req,classname='rf_validation');p=ET.SubElement(c,'properties');ET.SubElement(p,'property',name='requirement',value=req);ET.SubElement(c,'skipped',message='Simulation not completed')
  continue
 metrics=comparison['grids'][grid]
 evidence=f'runs/jlc20mil/{grid}-validated.s3p'
 sha=hashlib.sha256((ROOT/evidence).read_bytes()).hexdigest()
 for req,title,key,predicate,label in checks:
  value=metrics[key];case(s,grid+'_'+req,req,'simulation',predicate(value),f'{label}: {value}; source={evidence}; sha256={sha}; metrics=runs/jlc20mil/comparison.json#/grids/{grid}/{key}')
drc=json.loads((ROOT/'output/test-board/drc.json').read_text())
s=ET.SubElement(suites,'testsuite',name='board')
model['requirements'] += [
 {'id':'REQ-8','title':'40 x 36 mm two-layer RO4350B coupon with 0.51 mm core','satisfies':['UN-2'],'method':'TM-2'},
 {'id':'REQ-9','title':'Three 1092-03A-6 2.92 mm edge-launch footprints and microstrip feeds','satisfies':['UN-2'],'method':'TM-2'},
 {'id':'REQ-10','title':'Zero native KiCad DRC violations and unconnected items','satisfies':['UN-2'],'method':'TM-2'},
 {'id':'REQ-11','title':'Complete fixture meets RF limits at calibrated connector reference planes','satisfies':['UN-1','UN-2'],'method':'TM-3','description':'Not simulated or measured: launches, feeds, packaged resistor, finish and tolerances require bench verification.'},
 {'id':'REQ-12','title':'Qualify 5 W coherent combining under specified thermal conditions','satisfies':['UN-1'],'method':'TM-4','description':'No power or thermal qualification. Present resistor is intended for small-signal VNA tests only.'}]
model['requirements'] += [
 {'id':'REQ-13','title':'Whole populated assembly meets every RF acceptance limit at the three coaxial connector planes','satisfies':['UN-1','UN-2'],'method':'TM-5','description':'Mandatory release gate in spec.json assembly_validation. Include fixture losses and actual feeds/bends, launches, finite board, ground/vias and packaged resistor. DUT-only results do not satisfy this requirement.'},
 {'id':'REQ-14','title':'Assembly model covers actual geometry, materials, contacts and package parasitics with qualified provenance','satisfies':['UN-2'],'method':'TM-6','description':'Include every required_model_scope item in spec.json; missing or idealized launch/package models block assembly validation.'},
 {'id':'REQ-15','title':'Whole-assembly RF results have mesh, time-domain and tolerance convergence evidence','satisfies':['UN-3'],'method':'TM-5','description':'Three meshes, configured finest-pair error bounds, converged excitations, numerical checks and vendor-supported tolerance cases required by spec.json.'}]
assembly=json.loads((out/'assembly-validation.json').read_text())
assembly_suite=ET.SubElement(suites,'testsuite',name='assembly')
assembly_cases={13:'full_assembly_rf_acceptance',14:'assembly_model_scope',15:'mesh_and_tolerance_convergence'}
for n,name in assembly_cases.items():
 c=ET.SubElement(assembly_suite,'testcase',name=name,classname='assembly_validation')
 props=ET.SubElement(c,'properties')
 for key,value in [('requirement','REQ-'+str(n)),('level','inspection' if n==14 else 'simulation'),('artifact.spec_sha256',assembly['spec_sha256']),('artifact.board_sha256',assembly['board_sha256'])]:
  ET.SubElement(props,'property',name=key,value=value)
 reason='Whole-assembly simulation not run: '+'; '.join(assembly['blockers'])
 ET.SubElement(c,'skipped',message=reason)
 ET.SubElement(c,'system-out').text='reports/assembly-validation.json; spec.json#/assembly_validation; '+reason
board=(ROOT/'output/test-board/rf-combiner-test.kicad_pcb').read_text()
case(s,'core_and_outline','REQ-8','inspection','(thickness 0.51)' in board and '(material "RO4350B")' in board,'output/test-board/rf-combiner-test.kicad_pcb; outline dimensions: output/test-board/geometry.json. Core .51 mm, nominal finished thickness .65 mm; stackup requires fab confirmation.')
geom=json.loads((ROOT/'output/test-board/geometry.json').read_text())
case(s,'launch_footprints','REQ-9','inspection',geom['connector']=='1092-03A-6' and len(geom['ports'])==3,'output/test-board/geometry.json; output/test-board/BOM.csv; source mechanical drawing reference/1092-03A-6.pdf. Inspection does not verify launch RF performance.')
case(s,'native_drc','REQ-10','inspection',not drc['violations'] and not drc['unconnected_items'],'output/test-board/drc.json: violations='+str(len(drc['violations']))+', unconnected='+str(len(drc['unconnected_items'])))
for req in model['requirements']:
 n=int(req['id'].split('-')[1])
 if n<=7:
  names=['rf_validation::'+g+'_'+req['id'] for g in ['coarse','fine','finer']]
 elif n>=13:
  names=['assembly_validation::'+assembly_cases[n]]
 elif n<=10:
  names=['rf_validation::'+{8:'core_and_outline',9:'launch_footprints',10:'native_drc'}[n]]
 else:
  continue
 req['verified_by']=[{'target':'//:validation','cases':names}]
# JSON is valid YAML 1.2 and accepted by rules_requirements.
(ROOT/'requirements/model.yaml').write_text(json.dumps(model,indent=2)+'\n')
ET.indent(suites)
(out/'testlogs/validation').mkdir(parents=True,exist_ok=True)
ET.ElementTree(suites).write(out/'testlogs/validation/test.xml',encoding='utf-8',xml_declaration=True)
rows=[]
for name,m in comparison['grids'].items():
 rows.append(f"| {name} | {m['pitch_mm']:.3f} | {min(m['return_loss_min_db_per_port']):.3f} | {m['isolation_min_db']:.3f} | {m['excess_loss_max_db']:.3f} | {m['coherent_combining_loss_max_db']:.3f} | {'PASS' if m['meets_datasheet_small_signal_limits'] else 'FAIL'} |")
text='''# Validation of revision A

**Overall disposition: FAIL — experimental small-signal coupon; PDW07630 equivalence is not established.**

**Whole-assembly validation is BLOCKED and has not run.** See [assembly status](assembly-validation.json) and the mandatory [project spec](../spec.json). DUT-only results cannot release the populated board.

The numerical results below assess only the exported DUT copper, not the populated assembly or only the optimizer's density model. Its results supersede the earlier optimizer summary. The reference planes are the three design-window boundaries, with 50 ohm renormalization, not the fixture connectors. Each sweep has 81 points over 24–32 GHz.

| Grid | Pitch mm | Worst return loss dB (>=15) | Isolation dB (>=14) | Excess loss dB (<=0.7) | Coherent combining loss dB (<=0.7) | Result |
|---|---:|---:|---:|---:|---:|---|
'''+ '\n'.join(rows)+'''

The grid-by-grid data and individual-port metrics are in [comparison.json](../runs/jlc20mil/comparison.json). Raw simulation results: [coarse Touchstone](../runs/jlc20mil/coarse-validated.s3p), [fine Touchstone](../runs/jlc20mil/fine-validated.s3p), [finer Touchstone](../runs/jlc20mil/finer-validated.s3p). The corresponding NPZ files preserve complex S matrices, frequencies and rasterized copper. [Validation log](../validation.log) records mesh runtimes and backend. [validate_design.py](../validate_design.py) defines the procedure and acceptance thresholds. [Evidence XML](testlogs/validation/test.xml) references each simulation file by path and SHA-256, with one requirement per case.

Return loss and excess loss fail on the completed grids. Isolation, amplitude balance, phase balance and passivity pass. Mirror symmetry enforces nearly exact balance in this ideal model; it does not establish manufactured balance. Grid refinement is sensitivity evidence, not an assertion that the simulation is converged or matches hardware.

The optimizer used more demanding targets (20 dB return loss, 17 dB isolation, 0.5 dB excess loss) and did not meet them. It completed 73 iterations and mechanically selected iteration 25. See [optimizer result](../runs/jlc20mil/result.json), [history](../runs/jlc20mil/history.json) and [optimization log](../optimization.log). Its internal response differs from exported-polygon re-simulation; no claim is made that the export preserves the internal model's electrical response.

![Grid comparison](simulation-comparison.png)

## Dependency reproducibility

YAPNR is fetched as a pinned external dependency ([declaration](../dependencies/yapnr.json), [Dockerfile](../Dockerfile)). The original image omits RF export modules; [upstream issue #96](https://github.com/Studio-Fug/yapnr/issues/96) tracks the packaging fix. [Dependency smoke check](dependency-smoke.json) re-runs the coarse sweep outside the source checkout and compares its complex S matrix with the original committed simulation. The simulation artifacts and RF acceptance failures are unchanged.

## Board verification

[Native KiCad 10.0.6 DRC](../output/test-board/drc.json): zero violations and zero unconnected items. This verifies layout rules and DC connectivity, not microwave performance. The main footprint polygon is represented as a custom-pad primitive in the board so it participates in KiCad connectivity; its polygon coordinates are preserved (verified by [exact coordinate comparison](board-geometry.json), including floating islands). [Board builder](../build_board.py) records this conversion. The optimized footprint's own minimum-width/space check is in result.json under drc.

## Limitations and outstanding validation

- Ideal 100 ohm lumped resistor; no CH02016 package or solder parasitics.
- Zero-thickness smooth copper sheet; no ENIG, copper roughness, plating variation or manufacturing tolerance model.
- Infinite substrate and ground approximation; fixture traces, connector launches, mounting holes and board edges are excluded from RF simulation.
- No measured S parameters, calibrated fixture de-embedding, power handling or thermal qualification. The 5 W combining rating of the reference part is not established for this coupon.
- JLC material availability and finished stackup must be confirmed when quoting. Connector mounting and resistor land compatibility require assembly review.

The rules_requirements [traceability report](traceability.md), [machine report](traceability.json), [HTML report](traceability.html) and [gap queue](gaps.json) preserve failures and unverified bench requirements. Passing simulation evidence has simulation rigor only; it does not verify the complete fixture.
'''
(out/'validation.md').write_text(text)
# Hashes bind every report to the exact committed design/simulation artifacts.
paths=[ROOT/'spec.json',ROOT/'specs/dut-optimization.json',out/'assembly-validation.json',ROOT/'models/resistor/CH02016F_P_100R.s2p',run/'footprint.kicad_mod',run/'result.json',run/'comparison.json',ROOT/'output/test-board/rf-combiner-test.kicad_pcb',ROOT/'output/test-board/drc.json']+list(run.glob('*-validated.s3p'))+list(run.glob('*-validated.npz'))
(out/'artifact-manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')
print('Wrote model, evidence, report and artifact manifest.')
