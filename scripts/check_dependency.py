"""Reproduce the committed coarse simulation using the externally fetched dependency."""
import json
from pathlib import Path
import numpy as np
from yapnr.rf.validate import resimulate
from yapnr.rf.fdtd.native_kernel import status
root=Path(__file__).resolve().parents[1]
old=np.load(root/'runs/jlc20mil/coarse-validated.npz')
sw=resimulate(str(root/'runs/jlc20mil'),refine=1,n_sub=4,freqs=old['freqs'],log=lambda s:print(s,flush=True))
error=float(np.max(np.abs(sw['s']-old['s'])))
assert np.array_equal(sw['s'],old['s']),f'S-matrix differs: {error}'
report={'passed':True,'procedure':'Re-simulate exported footprint at refine=1, n_sub=4, 81 points with fetched external dependency, outside source checkout','reference':'runs/jlc20mil/coarse-validated.npz','max_absolute_s_difference':error,'bit_identical':True,'native':status(),'dependency':'dependencies/yapnr.json'}
(root/'reports/dependency-smoke.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
