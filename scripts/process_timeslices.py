"""Script to generate ERFs from time slice experiments."""

import glob
import os
import pickle
import warnings

from tqdm.auto import tqdm
import iris
from iris.util import equalise_attributes
import iris.coord_categorisation as cat
import numpy as np

iris.FUTURE.date_microseconds = True

datadir = "/user/brussel/111/vsc11139/data_vo/CMIP6/RFMIP/input"

models = [
    "ACCESS-CM2",
    "ACCESS-ESM1-5",
    "CanESM5",
    "CESM2",
    "CNRM-CM6-1",
    "CNRM-ESM2-1",
    "EC-Earth3",
    "GFDL-CM4",
    "GFDL-ESM4",
    "GISS-E2-1-G",
    "HadGEM3-GC31-LL",
    "IPSL-CM6A-LR",
    "IPSL-CM6A-LR-INCA",
    "MIROC6",
    "MPI-ESM-1-2-HAM",
    "MPI-ESM1-2-LR",
    "MRI-ESM2-0",
    "NorESM2-LM",
    "NorESM2-MM",
    "UKESM1-0-LL",
]

runids = {
    "ACCESS-CM2": ["r1i1p1f1"],
    "ACCESS-ESM1-5": ["r1i1p1f1"],
    "CanESM5": ["r1i1p2f1"],
    "CESM2": ["r1i1p1f1"],
    "CNRM-CM6-1": ["r1i1p1f2"],
    "CNRM-ESM2-1": ["r1i1p1f2"],
    "EC-Earth3": ["r1i1p1f1"],
    "GFDL-CM4": ["r1i1p1f1"],
    "GFDL-ESM4": ["r1i1p1f1"],
    "GISS-E2-1-G": ["r1i1p1f1", "r1i1p3f1"],  # Note these are practically different models
    "HadGEM3-GC31-LL": ["r1i1p1f3"],
    "IPSL-CM6A-LR": ["r1i1p1f1", "r2i1p1f1", "r3i1p1f1", "r4i1p1f1"],
    "IPSL-CM6A-LR-INCA": ["r1i1p1f1"],
    "MIROC6": ["r1i1p1f1"],
    "MPI-ESM-1-2-HAM": ["r1i1p1f1"],
    "MPI-ESM1-2-LR": ["r1i1p1f1"],
    "MRI-ESM2-0": ["r1i1p1f1"],
    "NorESM2-LM": ["r1i1p2f1"],
    "NorESM2-MM": ["r1i1p1f1"],
    "UKESM1-0-LL": ["r1i1p1f4"],
}

variables = ["rsdt", "rsut", "rlut"]

experiments = ["control", "ghg", "lu", "aer", "anthro", "4xCO2"]

warnings.simplefilter("ignore")
output = {}
for model in tqdm(models):
    output[model] = {}
    for runid in runids[model]:
        output[model][runid] = {}
        for experiment in experiments:
            tempoutput = {}
            output[model][runid][experiment] = {}
            for variable in variables:
                source_files = glob.glob(f"{datadir}/{variable}_*_{model}_piClim-{experiment}_{runid}*.nc")
                if len(source_files)>0:
                    cubes = iris.load(source_files)
                    equalise_attributes(cubes)
                    cube = cubes.concatenate_cube()
                    for coord in ['latitude', 'longitude']:
                        if not cube.coord(coord).has_bounds():
                            cube.coord(coord).guess_bounds()
                    area_weights = iris.analysis.cartography.area_weights(cube)
                    cat.add_year(cube, 'time', name='year')
                    cube_gm = cube.collapsed(['latitude', 'longitude'], iris.analysis.MEAN, weights=area_weights)
                    cube_agm = cube_gm.aggregated_by('year', iris.analysis.MEAN)
                    tempoutput[variable] = cube_agm.data
                else:
                    tempoutput[variable] = np.nan
            output[model][runid][experiment] = tempoutput['rsdt'] - tempoutput['rsut'] - tempoutput['rlut']
            if np.isscalar(output[model][runid][experiment]) and np.isnan(output[model][runid][experiment]):
                del output[model][runid][experiment]

os.makedirs('../output', exist_ok=True)

with open('../output/timeslice.pkl', 'wb') as handle:
    pickle.dump(output, handle, protocol=pickle.HIGHEST_PROTOCOL)
