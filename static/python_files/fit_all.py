
# Importing built-in modules

import numpy as np
from scipy.signal import find_peaks as peak
from pathlib import Path as pt
import json, sys

from FELion_definitions import read_dat_file

def fit_all_peaks(filename, norm_method, prominence=None, width=None, height=None, fitall=False):
    wn, inten = read_dat_file(filename, norm_method)

    indices, _ = peak(inten, prominence=prominence, width=width, height=height)

    if prominence is not None: 
        
        prominences = _["prominences"]
        left_bases = _["left_bases"]
        right_bases = _["right_bases"]
        wn_left = wn[left_bases]
        wn_right = wn[right_bases]
        wn_range = np.array([wn_left, wn_right]).T

    wn_ = list(wn[indices])
    inten_ = list(inten[indices])

    data = {
        "x":wn_, "y":inten_, "name":"peaks", "mode":"markers",
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

    prominence = args[3]
    if prominence == "": prominence = None
    else: prominence = float(prominence)

    fitall = args[4]
    if fitall == "true": fitall = True
    else: fitall = False

    width = args[5]
    if width == "": width = None
    else: width = float(width)

    height = args[6]
    if height == "": height = None
    else: height = float(height)
    
    fit_all_peaks(filename, norm_method, prominence, width, height, fitall)