
# Importing Modules
import json
from pathlib import Path as pt
import numpy as np
import sys
from pathlib import Path as pt

colors = [
    (31, 119, 180),
    (174, 199, 232),
    (255, 127, 14),
    (255, 187, 120),
    (44, 160, 44),
    (152, 223, 138),
    (214, 39, 40),
    (255, 152, 150),
    (148, 103, 189),
    (197, 176, 213),
    (140, 86, 75),
    (196, 156, 148),
    (227, 119, 194),
    (247, 182, 210),
    (127, 127, 127),
    (199, 199, 199),
    (188, 189, 34),
    (219, 219, 141),
    (23, 190, 207),
    (158, 218, 229),
]

def gaussian(x, A, sig, center):
    return A*np.exp(-0.5*((x-center)/sig)**2)


def exp_theory(theoryfiles, location, norm_method, sigma, scale):

    location = pt(location)

    if location.name is "DATA": datfile_location = location.parent/"EXPORT"
    else: datfile_location = location/"EXPORT"

    xs, ys = np.genfromtxt(f"{datfile_location}/averaged_{norm_method}.dat").T

    data = {"line_simulation":{}, "averaged": {
                "x": list(xs), "y": list(ys),  "name": "Exp",
                "mode": "lines", "marker": {"color": "black"},
        }}

    for theoryfile in theoryfiles:

        theoryfile = pt(theoryfile)

        x, y = np.genfromtxt(theoryfile).T[:2]
        x = x*scale

        norm_factor = ys.max()/y.max()
        y = norm_factor*y

        theory_x, theory_y = [], []
        for wn, inten in zip(x, y):

            size = 1000

            diff = 4*sigma
            x = np.linspace(wn - diff, wn + diff, size)

            y = gaussian(x, inten, sigma, wn)
            theory_x = np.append(theory_x, x)
            theory_y = np.append(theory_y, y)

        data["line_simulation"][f"{theoryfile.name}"] = {
                "x":list(theory_x), "y":list(theory_y),  "name":f"{theoryfile.stem}", "fill":"tozerox"
            }


    data_tosend = json.dumps(data)
    print(data_tosend)

if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")

    theory_file = args[0:-4]

    norm_method = args[-4]
    norm_method = "log" if norm_method else "rel"

    sigma = float(args[-3])

    scale = float(args[-2])
    location = args[-1]
    exp_theory(theory_file, location, norm_method, sigma, scale)
