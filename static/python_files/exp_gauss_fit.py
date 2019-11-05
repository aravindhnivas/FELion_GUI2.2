
# Importing Modules
import json
from pathlib import Path as pt
import sys

# FELion tkinter figure module
from FELion_widgets import FELion_Tk

# Data analysis
import numpy as np
from lmfit.models import GaussianModel

def exp_fit(location, norm_method, start_wn, end_wn, output_filename="averaged", tkplot=False):

    if location.name is "DATA": datfile_location = location.parent/"EXPORT"
    else: datfile_location = location/"EXPORT"

    wn, inten = np.genfromtxt(f"{datfile_location}/{output_filename}_{norm_method}.dat").T
    index = np.logical_and(wn > start_wn, wn < end_wn)
    wn = wn[index]
    inten = inten[index]
    model = GaussianModel()

    guess = model.guess(inten, x=wn)

    guess_values = guess.valuesdict()
    fit = model.fit(inten, x=wn, amplitude = guess_values['amplitude'], center = guess_values['center'],  sigma = guess_values['sigma'])

    fit_data = fit.best_fit
    line_freq_fit = fit.best_values['center']
    FWHM = lambda sigma: 2*sigma*np.sqrt(2*np.log(2))

    sigma = fit.best_values['sigma']

    fwhm = FWHM(sigma)

    amplitude = fit_data.max()

    _sig = "\u03C3"
    _del = "\u0394"
    
    data = {

        "fit": {"x":list(wn), "y":list(fit_data), "name":f"Fit: {line_freq_fit:.2f}, {_sig}: {sigma:.2f}, {_del}: {fwhm:.2f}", "mode": "lines", "line": {"color": "black"}},
        "line": {"type":"line", "x0":line_freq_fit, "x1":line_freq_fit, "y0":0, "y1":amplitude, "line":{"color":"black"}}

    }

    filename = f"{output_filename}_{norm_method}.expfit"
    expfile = datfile_location/filename

    
    with open(expfile, "a") as f:
        f.write(f"{line_freq_fit:.4f}\t{sigma:.4f}\t{fwhm:.4f}\t{amplitude:.4f}\n")

    data_tosend = json.dumps(data)
    print(data_tosend)


if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    start_wn = float(args[-2])
    end_wn = float(args[-1])
    location = pt(args[-3])
    norm_method = args[-4]

    output_filename = args[-5]
    # print(args)

    exp_fit(location, norm_method, start_wn, end_wn, output_filename)