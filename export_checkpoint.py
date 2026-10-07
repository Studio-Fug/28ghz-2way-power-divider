"""Export a snapshot of the optimizer's mechanically selected best binary candidate."""
import json
import shutil
import numpy as np
from pathlib import Path
from yapnr.rf.driver import Optimizer
from yapnr.rf.problem import Problem
from yapnr.rf.spec import Spec
from yapnr.rf.export import report
from yapnr.rf.export.kicad import write_footprint

src=Path('runs/jlc20mil')
dst=Path('runs/preview')
dst.mkdir(exist_ok=True)
for name in ('checkpoint.npz','history.json','frames.npz','spec.json'):
    shutil.copyfile(src/name,dst/name)
spec=Spec.load(str(src/'spec.json'))
prob=Problem(spec,cache_dir=str(src/'cache'),log=lambda s:print(s,flush=True))
opt=Optimizer(prob,out_dir=str(dst),log=lambda s:print(s,flush=True))
opt.load_checkpoint()
x=opt.state.best_x if opt.state.best_x is not None else opt.state.x
raw=prob.param.rho_bar(x,float('inf'))
binary,repair=report.exported_binary(prob,raw)
fp,_=report.footprint_of(prob,binary)
write_footprint(fp,str(dst/'footprint.kicad_mod'))
(dst/'preview.json').write_text(json.dumps({'best_t':opt.state.best_t,
    'best_iteration':opt.state.best_iteration,'repair':repair,'status':'in-progress preview'},indent=2)+'\n')
