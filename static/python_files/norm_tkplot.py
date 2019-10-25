
# Built-In modules
import sys
from pathlib import Path as pt

# FELion tkinter figure module
from FELion_widgets import FELion_Tk

# Data analysis modules
import numpy as np

def main(felixfiles, location, norm_method, index):

    dat_location = location / "EXPORT"
    widget = FELion_Tk(title="Felix Averaged plot", location=location/"OUT")
    fig, canvas = widget.Figure()

    if norm_method=="Relative": ylabel = "Relative Depletion (%)"
    else: ylabel = "Norm. Intensity"

    ax = widget.make_figure_layout(title="Felix Averaged plot", xaxis="Wavenumber $cm^{-1}$", yaxis=ylabel, yscale="linear", savename="felix_averaged")
    datfiles = [dat_location/f"{filename.stem}.dat" for filename in felixfiles]

    avgfile = dat_location/f"averaged_{norm_method}.dat"
    wn, inten  = np.genfromtxt(avgfile).T
    ax.plot(wn, inten, "k.-", label="Averaged")

    print(f"felix dat files: {datfiles}\nAveraged file: {avgfile}")
    for i, datfile in enumerate(datfiles):
        data = np.genfromtxt(datfile).T
        wn, inten = data[0], data[index]
        ax.plot(wn, inten, ".", label=f"{felixfiles[i].name}")
    widget.plot_legend = ax.legend()
    widget.mainloop()

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    filenames = args[0:-1]
    norm_method = args[-1]
    
    filenames = [pt(i) for i in filenames]
    location = filenames[0].parent

    if location.name is "DATA":
        location = location.parent
    
    if norm_method == "Log": index = 1
    else: index = 3
    main(filenames, location, norm_method, index)