"""Fail closed until a complete assembly model and execution backend exist."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
spec=json.loads((ROOT/'spec.json').read_text());v=spec['assembly_validation']
blockers=[]
if not v['assembly_models']['connector']['geometry_or_em_model']: blockers.append('No qualified 1092-03A-6 internal RF geometry/model')
if not v['assembly_models']['resistor']['qualified']: blockers.append('Resistor S-parameter reference planes, mounting and normalization not qualified')
if not v['assembly_models']['materials']['qualified_properties']: blockers.append('Full assembly loss/material properties and fabrication tolerances not qualified')
if not v['solver']['backend'] or not v['solver']['adapter']: blockers.append('No supported minimal-code YAPNR assembly SSoT/adapter configured; openEMS and PALACE engines are suitable, but integration and import fidelity gaps are tracked in issue #97')
report={'schema':'rf-combiner-assembly-validation/1','status':'BLOCKED' if blockers else 'NOT_RUN','simulation_run':False,'validated':False,'spec':'spec.json','spec_sha256':hashlib.sha256((ROOT/'spec.json').read_bytes()).hexdigest(),'reference_planes':v['reference_planes'],'board':spec['design_artifacts']['board'],'board_sha256':hashlib.sha256((ROOT/spec['design_artifacts']['board']).read_bytes()).hexdigest(),'blockers':blockers,'required_evidence':v['required_evidence'],'dut_results':'runs/jlc20mil/comparison.json','dut_results_satisfy_assembly_gate':False}
path=ROOT/v['report'];path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
# Readiness alone cannot grant validation, even when model blockers are resolved.
raise SystemExit(2 if blockers else 3)
