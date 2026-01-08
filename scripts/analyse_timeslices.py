"""Script to generate ERFs from time slice experiments."""

import copy
import os
import pickle

import matplotlib.pyplot as pl
import numpy as np

with open('../output/timeslice.pkl', 'rb') as handle:
    rfmip_data = pickle.load(handle)

pl.style.use("../defaults.mplstyle")

# don't forget to exclude first few years
# regardless of experiment, just take the last 15

experiments = ["4xCO2", "ghg", "aer", "lu", "anthro"]

rfmip_tier1_means = {}

for experiment in experiments:
    rfmip_tier1_means[experiment] = {}
    for model in rfmip_data:
        rfmip_tier1_means[experiment][model] = {}
        for runid in rfmip_data[model]:
            if experiment in rfmip_data[model][runid]:
                rfmip_tier1_means[experiment][model][runid] = (
                    (
                        np.mean(rfmip_data[model][runid][experiment][-15:])
                    ) - (
                        np.mean(rfmip_data[model][runid]['control'])
                    )
                )

# Separate out the p1 and p3 from GISS and rename others
rfmip_tier1_means["aer"]["GISS-E2-1-G_p1"] = {}
rfmip_tier1_means["aer"]["GISS-E2-1-G_p1"]["r1i1p1f1"] = copy.deepcopy(rfmip_tier1_means["aer"]["GISS-E2-1-G"]["r1i1p1f1"])
rfmip_tier1_means["aer"]["GISS-E2-1-G_p3"] = {}
rfmip_tier1_means["aer"]["GISS-E2-1-G_p3"]["r1i1p3f1"] = copy.deepcopy(rfmip_tier1_means["aer"]["GISS-E2-1-G"]["r1i1p3f1"])

rfmip_tier1_means["anthro"]["GISS-E2-1-G_p1"] = copy.deepcopy(rfmip_tier1_means["anthro"]["GISS-E2-1-G"])
rfmip_tier1_means["ghg"]["GISS-E2-1-G_p1"] = copy.deepcopy(rfmip_tier1_means["ghg"]["GISS-E2-1-G"])
rfmip_tier1_means["lu"]["GISS-E2-1-G_p1"] = copy.deepcopy(rfmip_tier1_means["lu"]["GISS-E2-1-G"])
rfmip_tier1_means["4xCO2"]["GISS-E2-1-G_p1"] = copy.deepcopy(rfmip_tier1_means["4xCO2"]["GISS-E2-1-G"])

del rfmip_tier1_means["anthro"]["GISS-E2-1-G"]
del rfmip_tier1_means["ghg"]["GISS-E2-1-G"]
del rfmip_tier1_means["lu"]["GISS-E2-1-G"]
del rfmip_tier1_means["4xCO2"]["GISS-E2-1-G"]
del rfmip_tier1_means["aer"]["GISS-E2-1-G"]


expt_means = {}
for experiment in experiments:
    expt_means[experiment] = {}
    for model in rfmip_tier1_means[experiment]:
        n_runs = len(rfmip_tier1_means[experiment][model])
        if n_runs > 0:
            expt_means[experiment][model] = np.ones((n_runs)) * np.nan
            for irun, runid in enumerate(rfmip_tier1_means[experiment][model]):
                expt_means[experiment][model][irun] = rfmip_tier1_means[experiment][model][runid]
            expt_means[experiment][model] = np.mean(expt_means[experiment][model])


fig, ax = pl.subplots(1, 1, figsize=(9/2.54, 9/2.54))

for iexp, experiment in enumerate(experiments):
    data = np.array(list(expt_means[experiment].values()))
    # 1.4x CO2 for easy comparison - use 0.2266 from Smith et al. 2020
    label = experiment
    if experiment == "4xCO2":
        data = data * 0.2266
        label = "CO2"
    ax.scatter(np.ones_like(data) * iexp, data, color="#808080")
    ax.text(iexp, -1.8, label, ha="center", va="bottom")
ax.grid(axis='y')
ax.axes.get_xaxis().set_visible(False)
ax.set_ylabel("W m$^{-2}$")
ax.set_xlim(-0.5, 4.5)
fig.tight_layout()

os.makedirs('../plots', exist_ok=True)
pl.savefig("../plots/rfmip_tier1.png")
pl.savefig("../plots/rfmip_tier1.pdf")
