"""Script to generate ERFs from time slice experiments."""

import os
import pickle

import matplotlib.pyplot as pl
import numpy as np

with open('../output/timeslice.pkl', 'rb') as handle:
    rfmip_data = pickle.load(handle)


# don't forget to exclude first few years
# regardless of experiment, just take the last 15

rfmip_tier1_means = {}

for experiment in ["4xCO2", "ghg", "aer", "lu", "anthro"]:
    rfmip_tier1_means[experiment] = {}
    for model in rfmip_data:
        if experiment in
        for runid in rfmip_data[model]:
            if experiment in rfmip_data[model][runid]:
                print(
                    model, 
                    runid, 
                    experiment, 
                    (
                        np.mean(rfmip_data[model][runid][experiment][-15:])
                    ) - (
                        np.mean(rfmip_data[model][runid]['control'])
                    )
                )



os.makedirs('../plots', exist_ok=True)
