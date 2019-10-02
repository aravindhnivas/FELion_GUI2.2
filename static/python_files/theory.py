
# Importing Modules
import json
from pathlib import Path as pt
import numpy as np
import sys
from pathlib import Path as pt

def gaussian(x, A, sig, center):
    return A*np.exp(-0.5*((x-center)/sig)**2)

def exp_theory(theoryfile, felixfiles, norm_method, sigma, scale):

    felixfiles = [pt(felixfile) for felixfile in felixfiles]
    theoryfile = pt(theoryfile)

    if felixfiles[0].parent.name is "DATA":
        datfile_location = felixfiles[0].parent.parent/"EXPORT"
    else:
        datfile_location = felixfiles[0].parent/"EXPORT"

    xs, ys = np.genfromtxt(
        f"{datfile_location}/averaged_{norm_method}.dat").T

    x, y = np.genfromtxt(theoryfile).T[:2]

    x = x*scale
    
    norm_factor = ys.max()/y.max()
    y = norm_factor*y

    data = {"shapes": {}, "gauss_simulation":{},
            "averaged": {
            "x": list(xs), "y": list(ys),  "name": "Exp", "showlegend": True,
        "mode": "lines",
        "marker": {"color": "black"},
        "opacity": 0.7
    }}

    for wn, inten in zip(x, y):

        data["shapes"][f"shapes_{wn}"] = {"type": "line", "x0": wn, "y0": 0, "x1": wn, "y1": inten,
                                          "line": {
                                              "color": 'rgb(55, 128, 191)',
                                              "width": 3
                                          }}

        sig = sigma
        size = 1000

        x = np.random.normal(wn, sig, size)
        x = np.sort(x, axis=0)
        y = gaussian(x, inten, sig, wn)
        data["gauss_simulation"][f"{wn}_sim"] = {
            "x":list(x), "y":list(y), "type": "scatter",  "line": {"color": "rgb(55, 128, 191)"}, "showlegend":False
        }

    data_tosend = json.dumps(data)
    print(data_tosend)


if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")
    theory_file = args[0]
    norm_method = args[1]
    if(norm_method):
        norm_method="log" 
    else: norm_method="rel"

    sigma = float(args[2])

    scale = float(args[3])
    felixfiles = args[4:]

    exp_theory(theory_file, felixfiles, norm_method, sigma, scale)
