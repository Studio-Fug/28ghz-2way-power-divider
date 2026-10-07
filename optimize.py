"""Run the documented YAPNR adjoint density/MMA inverse-design workflow."""
import json
from pathlib import Path
from yapnr.rf.driver import design
from yapnr.rf.spec import Spec

if __name__ == '__main__':
    spec = Spec.load('spec.json')
    result = design(spec, 'runs/jlc20mil', log=lambda s: print(s, flush=True))
    print(json.dumps(result['optimizer'], indent=2), flush=True)
