
# Importing Modules
import json
from pathlib import Path as pt
import numpy as np
import sys
from pathlib import Path as pt

def gaussian(x, A, sig, center):
    return A*np.exp(-0.5*((x-center)/sig)**2)

def exp_theory(theoryfile, felixfiles, norm_method):

    felixfiles = [pt(felixfile) for felixfile in felixfiles]
    theoryfile = pt(theoryfile)

    if felixfiles[0].parent.name is "DATA":
        datfile_location = felixfiles[0].parent.parent/"EXPORT"
    else:
        datfile_location = felixfiles[0].parent/"EXPORT"

    xs, ys = np.genfromtxt(
        f"{datfile_location}/averaged_{norm_method}.dat").T

    try:
        x, y = np.genfromtxt(theoryfile).T[:2]
    except:
        raise Exception(
            "Please select a theory file with 2-column\nYou can add comments by adding # in the beginning of the sentences")

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

        sig = 10
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

    felixfiles = args[2:]

    exp_theory(theory_file, felixfiles, norm_method)
