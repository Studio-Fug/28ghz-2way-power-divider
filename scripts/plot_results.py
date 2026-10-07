"""Plot complex S-parameter validation artifacts (NumPy + Matplotlib)."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1]
fig,axs=plt.subplots(2,2,figsize=(11,7),sharex=True)
colors={'coarse':'#9aa5b1','fine':'#2878b5','finer':'#b84d24'}
for name,color in colors.items():
 path=root/f'runs/jlc20mil/{name}-validated.npz'
 if not path.exists(): continue
 data=np.load(path);s=data['s'];f=data['freqs']/1e9
 db=20*np.log10(np.maximum(abs(s),1e-15))
 axs[0,0].plot(f,-db[:,0,0],color=color,label=name+' SUM')
 axs[0,0].plot(f,-db[:,1,1],color=color,linestyle='--',label=name+' A/B')
 axs[0,1].plot(f,-db[:,2,1],color=color,label=name)
 excess=np.max(np.stack([-db[:,i,j]-10*np.log10(2) for i,j in [(1,0),(2,0),(0,1),(0,2)]],axis=1),axis=1)
 axs[1,0].plot(f,excess,color=color,label=name)
 axs[1,1].plot(f,-10*np.log10(abs((s[:,0,1]+s[:,0,2])/np.sqrt(2))**2),color=color,label=name)
for ax,title,ylabel,limit in [(axs[0,0],'Return loss','dB (higher is better)',15),(axs[0,1],'Output isolation','dB (higher is better)',14),(axs[1,0],'Worst-direction excess insertion loss','dB (lower is better)',.7),(axs[1,1],'Coherent combining loss','dB (lower is better)',.7)]:
 ax.set_title(title);ax.set_ylabel(ylabel);ax.axhline(limit,color='black',linestyle=':',label='requirement');ax.grid(alpha=.2);ax.legend(fontsize=8);ax.set_xlim(24,32)
for ax in axs[1]:ax.set_xlabel('Frequency (GHz)')
fig.suptitle('Revision A: exported DUT copper, 50 Ω, ideal resistor\nFixture launches/feeds excluded — RF acceptance FAIL',fontsize=12)
fig.tight_layout();fig.savefig(root/'reports/simulation-comparison.png',dpi=180)
