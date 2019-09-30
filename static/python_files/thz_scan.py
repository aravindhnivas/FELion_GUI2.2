# Importing modules
import numpy as np
import matplotlib.pyplot as plt
from lmfit.models import GaussianModel

from pathlib import Path as pt
import sys, json

def thz_plot(filename):

    filename = pt(filename)

    # Opening file and reading its content
    with open(filename, "r") as fileContents:
        file = fileContents.readlines()
    file = file[1:]
    #############################################

    # Resonce ON counts value
    resOn = []

    for line in file:
        if line.startswith("#"): break
        line = line.split("\n")[0].split("\t")[:-1]
        resOn.append(line)
        
    resOn = resOn[1:]
    #############################################

    # Resonce OFF counts value
    resOff = []
    start = False

    for line in file:
        if line.startswith("# freq"):
            start = True
            continue
        if start: 
            if line.startswith("#"): break
            line = line.split("\n")[0].split("\t")[:-1]
            resOff.append(line)
            
    resOff = resOff[1:]
    #############################################

    resOn = np.array(resOn, dtype=np.float)
    resOff = np.array(resOff, dtype=np.float)

    #############################################

    freq = resOn.T[0]
    depletion = (resOff.T[1:] - resOn.T[1:])/resOff.T[1:]
    depletion_counts = depletion.T.mean(axis=1)
    # depletion_error = depletion.T.std(axis=1)

    #############################################
    depletion_counts = depletion_counts*100

    ############## MODEL ####################

    model = GaussianModel()
    guess = model.guess(depletion_counts, x=freq)
    guess_values = guess.valuesdict()
    fit = model.fit(depletion_counts, x=freq, amplitude = guess_values['amplitude'], 
                    center = guess_values['center'], 
                    sigma = guess_values['sigma'], 
                    fwhm = guess_values['fwhm'], 
                    height = guess_values['height'])

    fit_data = fit.best_fit

    line_freq_fit = fit.best_values['center']
    ##########################################################################################
    FWHM = lambda sigma: 2*np.sqrt(2*np.log(2))*sigma
    Amplitude = lambda a, sigma: a/(sigma*np.sqrt(2*np.pi))
    sigma = fit.best_values['sigma']

    fwhm = FWHM(sigma)
    amplitude = Amplitude(fit.best_values['amplitude'], sigma)
    half_max = amplitude/2
    ##########################################################################################

    data = {
        "shapes": {
            "center": {
                "type":"line", "x0":line_freq_fit, "x1":line_freq_fit,
                "y0": 0, "y1":amplitude, "name":"test"
            },
            "fwhm": {
                "type":"line", "x0":line_freq_fit-fwhm/2, "x1":line_freq_fit+fwhm/2,
                "y0": half_max, "y1":half_max
            }
        },
        "text": {
            "x":[line_freq_fit-9e-5, line_freq_fit+1.2e-4],
            "y":[half_max*.7, half_max*.2],
            "text":[f"{fwhm*1e6:.1f} KHz",
                f"{line_freq_fit:.7f} GHz"],
            "mode":"text", "showlegend":False
        },
        "data": {
            "x": list(freq), "y": list(depletion_counts),  "name": "Data", "mode":'lines+markers', "opacity":0.7
        },
        "fit": {
             "x": list(freq), "y": list(fit_data),  "name": "Fitted", "type": "scatter",
        }
    }
    dataToSend = json.dumps(data)
    print(dataToSend)

    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
    ax.plot(freq, depletion_counts, ".", label="Data (~30${\mu}$W)")
    ax.plot(freq, fit_data, label="Fitted")
    ax.vlines(line_freq_fit, 0, amplitude, label=f'{line_freq_fit:.7f} GHz')
    ax.hlines(half_max, line_freq_fit-fwhm/2, line_freq_fit+fwhm/2, color="C2", label=f"FWHM: {fwhm*1e6:.1f}KHz")
    ax.grid()
    ax.set(title="CD$^{+}$: j=1-0 line", xlabel="Frequency (GHz)", ylabel="Depletion (%)")
    ax.ticklabel_format(useOffset=False)
    ax.legend()
    fig.savefig(filename.parent/f'{filename.stem}_thz.png')
    # plt.show()
    plt.close()

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    filename = args[0]
    thz_plot(filename)