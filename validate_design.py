"""Re-simulate exported polygons on three grids against the PDW07630 limits."""
import json
from pathlib import Path
import numpy as np
from yapnr.rf.validate import resimulate
from yapnr.rf.export.touchstone import write_touchstone

ROOT=Path('runs/jlc20mil')
report={'schema':'rf-combiner-validation/1','band_ghz':[24,32],
    'reference_ohms':50,'reference_planes':'three design-window boundaries',
    'limits':{'return_loss_min_db':15,'isolation_min_db':14,
              'excess_loss_max_db':.7,'amplitude_imbalance_max_db':.5,
              'phase_imbalance_max_deg':5},'grids':{},
    'assumptions':['Ideal 100 ohm lumped resistor; no package parasitics',
        'Zero-thickness smooth copper sheet; no soldermask or ENIG/roughness model',
        'Infinite substrate and solid ground; launch connectors and fixture feeds excluded',
        'Small-signal EM only; no 5 W combining power qualification']}
freqs=np.linspace(24,32,81)*1e9
for name,refine,n_sub in [('coarse',1,4),('fine',2,6),('finer',3,8)]:
    sw=resimulate(str(ROOT),refine=refine,n_sub=n_sub,freqs=freqs,
                  log=lambda s:print(s,flush=True))
    s=sw['s']; db=20*np.log10(np.maximum(np.abs(s),1e-15))
    diagonal=np.diagonal(db,axis1=1,axis2=2)
    rl=-diagonal.max(axis=0)
    isolation=-max(db[:,1,2].max(),db[:,2,1].max())
    losses=np.stack([-db[:,i,j]-10*np.log10(2) for i,j in [(1,0),(2,0),(0,1),(0,2)]],axis=1)
    amplitude=np.max(np.abs(db[:,1,0]-db[:,2,0]))
    phase=np.max(np.abs(np.angle(s[:,1,0]/s[:,2,0],deg=True)))
    # Two equal, in-phase inputs, each carrying half the total incident power.
    efficiency=np.abs((s[:,0,1]+s[:,0,2])/np.sqrt(2))**2
    coherent_loss=-10*np.log10(np.maximum(efficiency,1e-15))
    passive=min(float(np.linalg.eigvalsh(np.eye(3)-m.conj().T@m).min()) for m in s)
    reciprocal=float(np.max(np.abs(s-s.swapaxes(1,2))))
    metrics={'pitch_mm':.15/refine,'substrate_cells':n_sub,
        'return_loss_min_db_per_port':rl.tolist(),'isolation_min_db':float(isolation),
        'excess_loss_max_db':float(losses.max()),
        'coherent_combining_loss_max_db':float(coherent_loss.max()),
        'amplitude_imbalance_max_db':float(amplitude),'phase_imbalance_max_deg':float(phase),
        'passivity_margin_min':passive,'reciprocity_error_max':reciprocal,
        'wall_s':sw['wall_s'],'steps':{str(k):int(v) for k,v in sw['steps'].items()}}
    metrics['meets_datasheet_small_signal_limits']=bool(
        min(rl)>=15 and isolation>=14 and losses.max()<=.7 and
        coherent_loss.max()<=.7 and amplitude<=.5 and phase<=5 and passive>=-1e-3)
    report['grids'][name]=metrics
    write_touchstone(str(ROOT/f'{name}-validated.s3p'),freqs,s)
    np.savez(ROOT/f'{name}-validated.npz',freqs=freqs,s=s,mask=sw['mask'])
    (ROOT/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(name,json.dumps(metrics),flush=True)
report['passed']=all(m['meets_datasheet_small_signal_limits'] for m in report['grids'].values())
(ROOT/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
