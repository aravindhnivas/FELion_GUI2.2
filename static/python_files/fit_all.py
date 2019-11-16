
# Importing built-in modules
import numpy as np
from scipy.signal import find_peaks as peak
from pathlib import Path as pt
import json, sys
from FELion_definitions import read_dat_file

from exp_gauss_fit import exp_fit

def fit_all_peaks(filename, norm_method, prominence=None, width=None, height=None, fitall=False, overwrite=False):

    wn, inten = read_dat_file(filename, norm_method)
    indices, _ = peak(inten, prominence=prominence, width=width, height=height)

    _["wn_range"] = np.array([wn[_["left_bases"]], wn[_["right_bases"]]]).T

    for item in _:
        _[item] = _[item].tolist()

    wn_ = list(wn[indices])
    inten_ = list(inten[indices])
    
    data = {"data": {}, "extras": _, "annotations":{}}

    data["data"] = {
        "x":wn_, "y":inten_, "name":"peaks", "mode":"markers",
        "marker":{
            "color":"blue", "symbol": "star-triangle-up", "size": 12
        }
    }

    data["annotations"] = [
            {
            "x": x,
            "y": y,
            "xref": 'x',
            "yref": 'y',
            "text": f'{x:.2f}',
            "showarrow": True,
            "arrowhead": 2,
            "ax": -25,
            "ay": -40
        }
        for x, y in zip(wn_, inten_)
    ]
    dataToSend = [{"data": data["data"]}, {"extras":data["extras"]}, {"annotations":data["annotations"]}]
    if not fitall:
        dataJson = json.dumps(dataToSend)
        print(dataJson)

    else:

        location = filename.parent.parent
        output_filename = filename.stem

        fit_data = [{"data": data["data"]}, {"extras":data["extras"]}]

        filename = f"{output_filename}.expfit"
        datfile_location = location/"EXPORT"
        expfile = datfile_location/filename

        if overwrite: method = "w"
        else: method = "a"
        annotations = []
        get_data = []

        with open(expfile, method) as f:
            if overwrite: f.write(f"#Frequency\t#Freq_err\t#Sigma\t#Sigma_err\t#FWHM\t#FWHM_err\t#Amplitude\t#Amplitude_err\n")
            for wavelength in _["wn_range"]:

                get_data_temp, uline_freq, usigma, uamplitude, ufwhm = exp_fit(location, norm_method, wavelength[0], wavelength[1], output_filename, getvalue=True)
                annotate = {
                    "x": uline_freq.nominal_value, "y": uamplitude.nominal_value, "xref": 'x', "yref": 'y', "text": f'{uline_freq:.2uP}',
                    "showarrow": True, "arrowhead": 2, "ax": -25, "ay": -40
                }
                annotations.append(annotate)
                get_data.append(get_data_temp)
                f.write(f"{uline_freq.nominal_value:.4f}\t{uline_freq.std_dev:.4f}\t{usigma.nominal_value:.4f}\t{usigma.std_dev:.4f}\t{ufwhm.nominal_value:.4f}\t{ufwhm.std_dev:.4f}\t{uamplitude.nominal_value:.4f}\t{uamplitude.std_dev:.4f}\n")

        fit_data.append({"annotations":annotations})
        fit_data.append(get_data)

        dataJson = json.dumps(fit_data)
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


    overwrite = args[7]
    if overwrite == "true": overwrite = True
    else: overwrite = False
    
    fit_all_peaks(filename, norm_method, prominence, width, height, fitall, overwrite)