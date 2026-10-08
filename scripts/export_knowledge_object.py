"""Translate committed design/evidence into Knowledge's draft public-artifact model.

This creates a local payload, never uploads it, generates keys, or asserts bench evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def blob(name):return {'path':name,'data':(ROOT/name).read_bytes().hex()}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-commitments');ap.add_argument('--publisher',default='0'*64);ap.add_argument('--output',default='knowledge/payload.json');args=ap.parse_args()
 if len(args.publisher)!=64 or any(c not in '0123456789abcdef' for c in args.publisher):ap.error('publisher must be a lowercase 32-byte Ed25519 public key')
 model=json.loads((ROOT/'requirements/model.yaml').read_text())
 designs=['spec.json','specs/dut-optimization.json','requirements/model.yaml','requirements/verification.rrlock','output/test-board/rf-combiner-test.kicad_pcb','output/test-board/rf-combiner-test.kicad_pro','output/test-board/fp-lib-table','output/test-board/RF_Test.pretty/SWM_1092-03A-6_Left.kicad_mod','output/test-board/RF_Test.pretty/SWM_1092-03A-6_Right.kicad_mod','output/test-board/BOM.csv','output/test-board/geometry.json','output/test-board/board-top.png','output/test-board/rf-combiner-revA-fabrication.zip','runs/jlc20mil/footprint.kicad_mod','Dockerfile','dependencies/yapnr.json','requirements/requirements.txt','optimize.py','validate_design.py','build_board.py','run-container.sh','run-validation.sh','scripts/build-runtime.sh','scripts/check_assembly_readiness.py','scripts/report.sh','scripts/make_validation_report.py','FABRICATION.md','models/resistor/CH02016F_P_100R.s2p','models/resistor/provenance.json']
 records=['reports/validation.md','reports/traceability.json','reports/testlogs/validation/test.xml','reports/assembly-validation.json','reports/backend-capability-audit.json','reports/artifact-manifest.json','reports/board-geometry.json','reports/dependency-smoke.json','output/test-board/drc.json','runs/jlc20mil/comparison.json','runs/jlc20mil/result.json','validation.log']
 for grid in ['coarse','fine','finer']:records += [f'runs/jlc20mil/{grid}-validated.s3p',f'runs/jlc20mil/{grid}-validated.npz']
 origin={'repository':'https://github.com/Studio-Fug/28ghz-2way-power-divider','source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_visibility':'public','knowledge_repository':'https://github.com/Studio-Fug/knowledge','knowledge_revision':'25c50c9ac16f3195af54266eb8aae51b56b166e3','publication':'Public PoC candidate; prototype publisher identity, not independent verification','translation':'Publisher-reported mapping of existing simulation/inspection records, not independently authenticated testing','open_tool_gaps':['https://github.com/Studio-Fug/yapnr/issues/96','https://github.com/Studio-Fug/yapnr/issues/97']}
 record_blobs=[blob(n) for n in records]+[{'path':'knowledge-origin.json','data':canonical(origin).hex()}]
 rigor={n:('simulation' if n<=7 or n in [13,15] else 'software' if n==10 else 'physical' if n in [11,12] else 'analysis') for n in range(1,16)}
 steps=[
 {'id':'DUT-SIM','instructions':'Use the pinned YAPNR dependency, then run ./run-validation.sh. Re-simulate the exact exported DUT footprint on all three documented grids. This procedure excludes the fixture connectors and feeds.','acceptance':'Every DUT RF limit in spec/model and numerical passivity check must pass across 24-32 GHz; retain the complex S matrices and per-grid verdicts.'},
 {'id':'BOARD-INSPECTION','instructions':'Inspect the committed board, stackup, outline and mechanical connector lands against geometry.json, BOM and manufacturer drawings.','acceptance':'40 x 36 mm two-layer board, 0.51 mm RO4350B core, three specified 2.92 mm launch footprints; assembly inspection is not a manufactured-stackup measurement.'},
 {'id':'DRC','instructions':'Run native KiCad 10.0.6 DRC using --exit-code-violations on the committed board.','acceptance':'Zero violations and zero unconnected items.'},
 {'id':'ASSEMBLY-SIM','instructions':'Resolve qualified component models through the YAPNR-owned assembly SSoT and generate openEMS/PALACE models through supported adapters. Execute the whole populated assembly at all three coaxial connector planes. Currently blocked: see assembly-validation.json and issue #97.','acceptance':'All full-assembly scope, RF, model coverage, convergence and tolerance gates in spec.json pass. DUT-only results cannot substitute.'},
 {'id':'BENCH','instructions':'Assemble the actual board and perform calibrated three-port VNA measurements at the connector planes. This has not been performed.','acceptance':'The physical complete assembly meets its specified RF limits under recorded calibration/measurement conditions.'},
 {'id':'POWER','instructions':'Perform controlled coherent-input power and thermal qualification under specified operating conditions. This has not been performed.','acceptance':'Demonstrated 5 W coherent combining power qualification; small-signal simulation cannot substitute.'}]
 payload={'version':1,'publisher':args.publisher,'specification':{'title':'28 GHz two-way microstrip combiner / divider — experimental revision A','requirements':[{'id':r['id'],'text':r['title']+'; '+r.get('description','')+'; normative criteria: spec.json and requirements/model.yaml','required_rigor':rigor[int(r['id'].split('-')[1])]} for r in model['requirements']]},'design':[blob(n) for n in designs],'procedure':steps,'subject':{'kind':'design','identifier':'Studio-Fug/28ghz-2way-power-divider:revision-A','conditions':'Design scope only. 24-32 GHz, 50 ohm ports, 0.51 mm RO4350B core, three 2.92 mm launches. Existing EM records cover only the ideal-resistor DUT at design-window boundaries. Full populated assembly simulation is blocked and no physical specimen or power qualification exists. This local translation has no independent reporter authentication.'},'evidence':[],'records':record_blobs,'claims':[],'predecessors':[],'dependencies':[]}
 if args.source_commitments:
  sources=json.loads((ROOT/args.source_commitments).read_text())['sources']
  payload['version']=2;payload['sources']=sources
  for src in sources:
   if src['role']=='design': payload['design']=[b for b in payload['design'] if not (b['path']==src['subdirectory'] or b['path'].startswith(src['subdirectory']+'/'))]
   else: payload['records']=[b for b in payload['records'] if not (b['path']==src['subdirectory'] or b['path'].startswith(src['subdirectory']+'/'))]
  origin['source_revision']=sources[0]['revision']
  for b in payload['records']:
   if b['path']=='knowledge-origin.json':b['data']=canonical(origin).hex()
 subject={'context':'knowledge:verification-subject:v2' if args.source_commitments else 'knowledge:verification-subject:v1',**{k:payload[k] for k in ['specification','design','procedure','subject','dependencies']}}
 if args.source_commitments:subject['sources']=[s for s in payload['sources'] if s['role']=='design']
 digest=hashlib.sha256(canonical(subject)).hexdigest()
 comparison=json.loads((ROOT/'runs/jlc20mil/comparison.json').read_text())
 predicates={1:lambda m:min(m['return_loss_min_db_per_port'])>=15,2:lambda m:m['isolation_min_db']>=14,3:lambda m:m['excess_loss_max_db']<=.7,4:lambda m:m['amplitude_imbalance_max_db']<=.5,5:lambda m:m['phase_imbalance_max_deg']<=5,6:lambda m:m['coherent_combining_loss_max_db']<=.7,7:lambda m:m['passivity_margin_min']>=-.001}
 for n in range(1,11):
  req=f'REQ-{n}'
  if n<=7:
   passed=all(predicates[n](comparison['grids'][g]) for g in ['coarse','fine','finer']);step='DUT-SIM';refs=['runs/jlc20mil/comparison.json','reports/traceability.json']+[f'runs/jlc20mil/{g}-validated.s3p' for g in ['coarse','fine','finer']];notes='Existing three-grid exported-DUT simulation only; ideal resistor, no connector/fixture/finish model. This translation reports its applicability to the explicitly DUT-plane requirement and does not claim assembly validation or independent reproduction.'
  elif n<=9:
   passed=True;step='BOARD-INSPECTION';refs=['reports/traceability.json','reports/board-geometry.json'];notes='Existing CAD/mechanical inspection. Inspection is conservatively represented as analysis because Knowledge has no inspection rigor category; this is not physical verification.'
  else:
   drc=json.loads((ROOT/'output/test-board/drc.json').read_text());passed=not drc['violations'] and not drc['unconnected_items'];step='DRC';refs=['output/test-board/drc.json','reports/traceability.json'];notes='Native KiCad software DRC, not microwave validation. Tests are not rerun by this object export.'
  if args.source_commitments:
   refs=list(dict.fromkeys(next((s['path'] for s in payload['sources'] if s['role']=='record' and ref.startswith(s['subdirectory']+'/')),ref) for ref in refs))
  payload['evidence'].append({'id':f'E-{req}','subject_hash':digest,'requirements':[req],'step':step,'records':refs,'outcome':'pass' if passed else 'fail','rigor':rigor[n],'reporter':args.publisher,'origin':'publisher','reproduction_notes':notes})
 # Missing / blocked evidence is intentionally absent, not manufactured passing or failing evidence.
 payload['claims']=[
 {'kind':'capability','text':'Candidate two-way coherent RF combining and power division over 24-32 GHz; RF acceptance fails and complete assembly is unvalidated','aliases':['28 GHz combiner','two way power divider','Wilkinson combiner','combine RF signals'],'evidence':[f'E-REQ-{n}' for n in range(1,7)]},
 {'kind':'capability','text':'Balanced branches in the symmetric ideal DUT simulation','aliases':['amplitude balance','phase balance'],'evidence':['E-REQ-4','E-REQ-5']},
 {'kind':'constraint','text':'Specified 0.51 mm RO4350B core and three 2.92 mm edge-launch footprints','aliases':['RO4350B','2.92 mm connector','40 x 36 mm test board'],'evidence':['E-REQ-8','E-REQ-9']},
 {'kind':'constraint','text':'Complete-assembly validation requires YAPNR-owned SSoT and openEMS/PALACE adapters; currently blocked','aliases':['assembly validation','single source of truth'],'evidence':[]}]
 output=ROOT/args.output;output.parent.mkdir(parents=True,exist_ok=True);data=canonical(payload)+b'\n';assert len(data)<4*1024*1024;output.write_bytes(data)
 (output.parent/'draft-metadata.json').write_text(json.dumps({'schema':'knowledge-draft-metadata/1','subject_hash':digest,'payload_bytes':len(data),'design_files':len(designs),'record_files':len(record_blobs),'requirements':len(model['requirements']),'reported_pass_requirements':[e['requirements'][0] for e in payload['evidence'] if e['outcome']=='pass'],'reported_failed_requirements':[e['requirements'][0] for e in payload['evidence'] if e['outcome']=='fail'],'missing_requirements':['REQ-11','REQ-12','REQ-13','REQ-14','REQ-15'],'publisher_key_is_placeholder':args.publisher=='0'*64,'publication':'Public PoC draft; unsigned until explicitly sealed','origin':origin},indent=2)+'\n')
 print(json.dumps({'payload':str(output.relative_to(ROOT)),'subject_hash':digest,'bytes':len(data)}))
if __name__=='__main__':main()
