# Importing Modules
import json
from pathlib import Path as pt
import sys

# Data analysis
import numpy as np

# FELion module
from FELion_definitions import gauss_fit

def exp_fit(location, norm_method, start_wn, end_wn, output_filename="averaged", tkplot=False):

    if location.name is "DATA": datfile_location = location.parent/"EXPORT"
    else: datfile_location = location/"EXPORT"
    wn, inten = np.genfromtxt(f"{datfile_location}/{output_filename}_{norm_method}.dat").T

    # Getting data from the selected range
    index = np.logical_and(wn > start_wn, wn < end_wn)
    wn = wn[index]
    inten = inten[index]

    _sig = "\u03C3"
    _del = "\u0394"

    model = gauss_fit(wn, inten)
    fit_data, uline_freq, usigma, uamplitude, ufwhm = model.get_data()

    line_freq_fit = model.get_value(uline_freq)
    fwhm = model.get_value(ufwhm)
    amplitude = model.get_value(uamplitude)
    sigma = model.get_value(usigma)

    data = {

        "fit": {"x":list(wn), "y":list(fit_data), "name":f"{uline_freq:.2uP}; A: {uamplitude:.2uP}, {_del}: {ufwhm:.2uP}", "mode": "lines", "line": {"color": "black"}},
        "line": [
            {"type":"line", "x0":line_freq_fit, "x1":line_freq_fit, "y0":0, "y1":amplitude, "line":{"color":"black"}},
            {"type":"line", "x0":line_freq_fit-fwhm/2, "x1":line_freq_fit+fwhm/2, "y0":amplitude/2, "y1":amplitude/2, "line":{"color":"black", "dash":"dot"}}
        ]
    }

    filename = f"{output_filename}_{norm_method}.expfit"
    expfile = datfile_location/filename

    
    with open(expfile, "a") as f:
        f.write(f"{line_freq_fit:.4f}\t{uline_freq.std_dev:.4f}\t{sigma:.4f}\t{usigma.std_dev:.4f}\t{fwhm:.4f}\t{ufwhm.std_dev:.4f}\t{amplitude:.4f}\t{uamplitude.std_dev:.4f}\n")

    data_tosend = json.dumps(data)
    print(data_tosend)

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")

    start_wn = float(args[-2])
    end_wn = float(args[-1])

    location = pt(args[-3])
    norm_method = args[-4]
    output_filename = args[-5]
    
    exp_fit(location, norm_method, start_wn, end_wn, output_filename)