# System modules
import sys
import json
import os
from pathlib import Path as pt
import traceback

# Data analysis
import numpy as np

# FELion tkinter figure module
from FELion_widgets import FELion_Tk

def opoplot(opofiles, tkplot):

    if tkplot:
        
        widget = FELion_Tk(title="Mass spectrum", location=opofiles[0].parent)

        fig, canvas = widget.Figure()

        if len(opofiles) == 1: savename=opofiles[0].stem
        else: savename = "combined_masspec"
        ax = widget.make_figure_layout(title="Mass Spectrum", xaxis="Mass [u]", yaxis="Counts", yscale="log", savename=savename)

    else: data = {}
    for opofile in opofiles:

        wn, counts = np.genfromtxt(opofile).T

        # res, b0, trap = var_find(opofile)
        label = f"{opofile.stem}"

        if tkplot: ax.plot(wn, counts, label=label)
        
        else: data[opofile.stem] = {
            "x": list(wn), "y": list(counts), "name": label, "mode": "lines", "showlegend": True
        }

    if not tkplot:
        dataJson = json.dumps(data)
        print(dataJson)

    else:
        widget.plot_legend = ax.legend()

        widget.mainloop()

if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")
    opofiles = [pt(i) for i in args[:-1]]

    tkplot = args[-1]
    if tkplot == "plot": tkplot = True
    else: tkplot = False
    # print(args)
    opoplot(opofiles, tkplot)