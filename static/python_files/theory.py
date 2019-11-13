
# Importing Modules
import json
from pathlib import Path as pt
import sys
from pathlib import Path as pt

# FELion tkinter figure module
from FELion_widgets import FELion_Tk

# Data analysis
import numpy as np

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

def exp_theory(theoryfiles, location, norm_method, sigma, scale, tkplot, output_filename="averaged"):

    location = pt(location)

    if tkplot:
        
        widget = FELion_Tk(title="Exp. Vs Theory", location=theoryfiles[0].parent)
        fig, canvas = widget.Figure()
        if len(theoryfiles) == 1: savename=theoryfiles[0].stem
        else: savename = "Exp vs Theory"
        ax = widget.make_figure_layout(title="Experimental vs Theory", xaxis="Wavenumber $(cm^{-1})$", yaxis="counts", yscale="linear", savename=savename)

    if location.name is "DATA": datfile_location = location.parent/"EXPORT"
    else: datfile_location = location/"EXPORT"
    avgfile = datfile_location/f"{output_filename}.dat"

    read_data = np.genfromtxt(avgfile).T
    xs = read_data[0]

    if norm_method == "Log": ys = read_data[1]
    else: ys = read_data[2]
    # xs, ys = np.genfromtxt(avgfile).T

    if tkplot:
        ax.plot(xs, ys, "k-", label="Experiment")
    else:
        data = {"line_simulation":{}, "averaged": {
                    "x": list(xs), "y": list(ys),  "name": "Exp",
                    "mode": "lines", "marker": {"color": "black"},
            }}

    for theoryfile in theoryfiles:

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

        if tkplot:
            ax.fill(theory_x, theory_y, label=theoryfile.stem)
        else:
            data["line_simulation"][f"{theoryfile.name}"] = {
                    "x":list(theory_x), "y":list(theory_y),  "name":f"{theoryfile.stem}", "fill":"tozerox"
                }

    if not tkplot:

        dataJson = json.dumps(data)
        print(dataJson)

    else:
        widget.plot_legend = ax.legend()
        widget.mainloop()

    # data_tosend = json.dumps(data)
    # print(data_tosend)

if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")

    theoryfiles = [pt(i) for i in args[0:-6]]
    tkplot = args[-1]

    if tkplot == "plot": tkplot=True
    else: tkplot = False

    location = args[-2]
    scale = float(args[-3])
    sigma = float(args[-4])
    norm_method = args[-5]

    # output_filename = args[-6]
    # print(output_filename)
    exp_theory(theoryfiles, location, norm_method, sigma, scale, tkplot)