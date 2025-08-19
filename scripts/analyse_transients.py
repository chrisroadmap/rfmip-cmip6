"""Script to generate ERFs from time slice experiments."""

import copy
import os
import pickle

import matplotlib.pyplot as pl
import numpy as np

with open('../output/transient.pkl', 'rb') as handle:
    transient_data = pickle.load(handle)

with open('../output/timeslice.pkl', 'rb') as handle:
    timeslice_data = pickle.load(handle)

pl.style.use("../tier2.mplstyle")

experiments = ["histall", "histghg", "histaer", "histnat"]

control_runids = {
    "CanESM5": ["r1i1p2f1"],
    "CNRM-CM6-1": ["r1i1p1f2"],
    "GFDL-CM4": ["r1i1p1f1"],
    "GISS-E2-1-G": ["r1i1p1f1"],
    "HadGEM3-GC31-LL": ["r1i1p1f3"],
    "IPSL-CM6A-LR": ["r1i1p1f1", "r2i1p1f1", "r3i1p1f1", "r4i1p1f1"],  # special case
    "MIROC6": ["r1i1p1f1"],
    "NorESM2-LM": ["r1i1p2f1"],
}

rfmip_tier1_means = {}
for experiment in ['control']:
    rfmip_tier1_means[experiment] = {}
    for model in control_runids:
        rfmip_tier1_means[experiment][model] = {}
        for runid in control_runids[model]:
            print(model, runid)
            rfmip_tier1_means[experiment][model][runid] = np.mean(timeslice_data[model][runid]['control'])

expt_tier1_means = {}
for experiment in ['control']:
    expt_tier1_means[experiment] = {}
    for model in rfmip_tier1_means[experiment]:
        n_runs = len(rfmip_tier1_means[experiment][model])
        if n_runs > 0:
            expt_tier1_means[experiment][model] = np.ones((n_runs)) * np.nan
            for irun, runid in enumerate(rfmip_tier1_means[experiment][model]):
                expt_tier1_means[experiment][model][irun] = rfmip_tier1_means[experiment][model][runid]
            expt_tier1_means[experiment][model] = np.mean(expt_tier1_means[experiment][model])

rfmip_tier2_means = {}

for experiment in experiments:
    rfmip_tier2_means[experiment] = {}
    for model in transient_data:
        rfmip_tier2_means[experiment][model] = {}
        for runid in transient_data[model]:
            print(model, runid, transient_data[model][runid])
            if experiment in transient_data[model][runid]:
                rfmip_tier2_means[experiment][model][runid] = (
                    transient_data[model][runid][experiment] - expt_tier1_means['control'][model]
                )


expt_tier2_means = {}
for experiment in experiments:
    expt_tier2_means[experiment] = {}
    for model in rfmip_tier2_means[experiment]:
        n_runs = len(rfmip_tier2_means[experiment][model])
        if n_runs > 0:
            for irun, runid in enumerate(rfmip_tier2_means[experiment][model]):
                if irun==0:
                    expt_tier2_means[experiment][model] = np.ones(
                        (rfmip_tier2_means[experiment][model][runid].shape[0], n_runs)
                    ) * np.nan
                expt_tier2_means[experiment][model][:, irun] = rfmip_tier2_means[experiment][model][runid]
            expt_tier2_means[experiment][model] = np.mean(expt_tier2_means[experiment][model], axis=1)


fig, ax = pl.subplots(2, 2, figsize=(18/2.54, 9/2.54))

for iexp, experiment in enumerate(experiments):
    i = iexp//2
    j = iexp%2
    for model in expt_tier2_means[experiment]:
        n_years = len(expt_tier2_means[experiment][model])
        last_year = 1850 + n_years
        ax[i,j].plot(np.arange(1850.5, last_year), expt_tier2_means[experiment][model], label=model)
    ax[i,j].set_title(experiment)
    ax[i,j].set_ylabel("W m$^{-2}$")
    ax[i,j].set_xlim(1850, 2101)
ax[0,1].legend(frameon=False, fontsize=5.5)
fig.tight_layout()

pl.show()

os.makedirs('../plots', exist_ok=True)
pl.savefig("../plots/rfmip_tier2.png")
pl.savefig("../plots/rfmip_tier2.pdf")
