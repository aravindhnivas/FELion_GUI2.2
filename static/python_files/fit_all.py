
# Importing built-in modules

import numpy as np
from scipy.signal import find_peaks as peak
from pathlib import Path as pt
import json, sys

# FELion modules
from FELion_definitions import read_dat_file

def fit_all_peaks(filename, norm_method, prominence=5, fitall=False):

    wn, inten = read_dat_file(filename, norm_method)

    indices, prominence_prop = peak(inten, prominence=prominence)

    prominences = list(prominence_prop["prominences"])
    left_bases = list(prominence_prop["left_bases"])
    right_bases = list(prominence_prop["right_bases"])

    wn_left = wn[left_bases]
    wn_right = wn[right_bases]
    wn_range = list(np.array([wn_left, wn_right]).T)

    wn_ = list(wn[indices])
    inten_ = list(inten[indices])

    data = {
        "x":list(wn_), "y":list(inten_), "name":"peaks", "mode":"markers",
        "marker":{
            "color":"blue", "symbol": "star-triangle-up", "size": int(12)
        }
    }

    dataJson = json.dumps(data)
    print(dataJson)

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")

    filename = args[0]

    location = pt(args[1])
    if location.name == "DATA": location = location.parent
    filename = location / f"EXPORT/{filename}.dat"

    norm_method = args[2]
    prominence = float(args[3])

    fitall = args[4]

    if fitall == "true": fitall = True
    else: fitall = False

    # print(fitall)

    fit_all_peaks(filename, norm_method, prominence, fitall)