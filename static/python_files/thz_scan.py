# Data analysis
import numpy as np
# from lmfit.models import VoigtModel

# Built-In modules
from pathlib import Path as pt
import sys, json, os

# FELion tkinter figure module
from FELion_widgets import FELion_Tk
from FELion_definitions import gauss_fit
from FELion_constants import colors

# #########################################################

def thz_plot(filename):
    with open(filename, "r") as fileContents: file = fileContents.readlines()
    file = file[1:]

    resOn = []

    for line in file:
        if line.startswith("#"): break
        line = line.split("\n")[0].split("\t")[:-1]
        resOn.append(line)
    resOn = resOn[1:]

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

    # depletion_error = depletion.T.std(axis=1)*100

    depletion_counts = depletion_counts*100
    iteraton = int(resOn[0].shape[0]-1)
    steps = int(round((freq[1]-freq[0])*1e6, 0))

    return freq, depletion_counts, f"{steps} KHz : {iteraton} cycles"

def binning(xs, ys, delta=1e-6):

    """
    Binns the data provided in xs and ys to bins of width delta
    output: binns, intensity 
    """

    # bins = np.arange(start, end, delta)
    # occurance = np.zeros(start, end, delta)
    BIN_STEP = delta
    BIN_START = xs.min()
    BIN_STOP = xs.max()

    indices = xs.argsort()
    datax = xs[indices]
    datay = ys[indices]

    # print("In total we have: ", len(datax), ' data points.')
    # do the binning of the data
    bins = np.arange(BIN_START, BIN_STOP, BIN_STEP)
    # print("Binning starts: ", BIN_START,
    #    ' with step: ', BIN_STEP, ' ENDS: ', BIN_STOP)

    bin_i = np.digitize(datax, bins)
    bin_a = np.zeros(len(bins) + 1)
    bin_occ = np.zeros(len(bins) + 1)

    for i in range(datay.size):
        bin_a[bin_i[i]] += datay[i]
        bin_occ[bin_i[i]] += 1

    binsx, data_binned = [], []
    for i in range(bin_occ.size - 1):
        if bin_occ[i] > 0:
            binsx.append(bins[i] - BIN_STEP / 2)
            data_binned.append(bin_a[i] / bin_occ[i])

    # non_zero_i = bin_occ > 0
    # binsx = bins[non_zero_i] - BIN_STEP/2
    # data_binned = bin_a[non_zero_i]/bin_occ[non_zero_i]

    # print("after binning", binsx, data_binned)
    binsx = np.array(binsx, dtype=np.float)
    data_binned = np.array(data_binned, dtype=np.float)
    return binsx, data_binned

def main(filenames, delta, tkplot, gamma=None):

    os.chdir(filenames[0].parent)

    if tkplot:
        widget = FELion_Tk(title="THz Scan", location=filenames[0].parent)
        fig, canvas = widget.Figure()
        if len(filenames) == 1: savename=filenames[0].stem
        else: savename = "averaged_thzScan"
        ax = widget.make_figure_layout(title="THz scan", xaxis="Frequency (GHz)", yaxis="Depletion (%)", savename=savename)
        
    else: data = {}

    xs, ys = [], []

    for i, filename in enumerate(filenames):
        filename = pt(filename)
        freq, depletion_counts, iteraton = thz_plot(filename)
        model = gauss_fit(freq, depletion_counts)
        fit_data, uline_freq, usigma, uamplitude, ufwhm = model.get_data()
        freq_fit = uline_freq.nominal_value
        freq_fit_err = uline_freq.std_dev*1e7
        
        if tkplot:
            ax.plot(freq, depletion_counts, f"C{i}.", label=f"{filename.name} [{iteraton}]")
            ax.plot(freq, fit_data, f"C{i}-", label=f"Fit.: {freq_fit:.7f} ({freq_fit_err:.0f}) [{ufwhm.nominal_value*1e6:.1f} KHz]")
        else:


            label = f"{filename.name}"
            data[label] = {"x": list(freq), "y": list(depletion_counts), "name": f"{label} [{iteraton}]", 
                "mode":'markers', "line":{"color":f"rgb{colors[i*2]}"}
            }

            label_fit = f"Fit: {freq_fit:.7f} ({freq_fit_err:.0f}) [{ufwhm.nominal_value*1e6:.1f} KHz]"
            data[f"{label}_fit"] = {"x": list(freq), "y": list(fit_data), "name": label_fit, 
                "mode": "lines", "line":{"color":f"rgb{colors[i*2]}"}
            }

        xs = np.append(xs, freq)
        ys = np.append(ys, depletion_counts)

    # Averaged
    binx, biny = binning(xs, ys, delta)
    
    model = gauss_fit(binx, biny)
    fit_data, uline_freq, usigma, uamplitude, ufwhm = model.get_data()

    sigma = usigma.nominal_value
    fwhm = ufwhm.nominal_value

    amplitude = uamplitude.nominal_value
    half_max = amplitude/2
    line_freq_fit = uline_freq.nominal_value
    freq_fit_err = uline_freq.std_dev*1e7

    with open(f"./averaged_thz.dat", "w") as f:
        f.write("#Frequency(in MHz)\t#Intensity\n")
        for freq, inten in zip(binx, fit_data):
            f.write(f"{freq*1e3}\t{inten}\n")

    label = f"Binned (delta={delta*1e9:.2f} Hz)"
    if tkplot: ax.plot(binx, biny, "k.", label=label)
    else:
        data["Averaged_exp"] = {
            "x": list(binx), "y": list(biny),  "name":label, "mode": "markers", "marker":{"color":"black"}
        }

    if tkplot:
        ax.plot(binx, fit_data, "k-", label=f"Fitted: {line_freq_fit:.7f} ({freq_fit_err:.0f}) [{fwhm*1e6:.1f} KHz]")
        ax.vlines(x=line_freq_fit, ymin=0, ymax=amplitude, zorder=10)
        ax.hlines(y=half_max, xmin=line_freq_fit-fwhm/2, xmax=line_freq_fit+fwhm/2, zorder=10)
        widget.plot_legend = ax.legend()

        widget.mainloop()

    else:

        data["Averaged_fit"] = {
            "x": list(binx), "y": list(fit_data),  "name": f"Fitted: {line_freq_fit:.7f} ({freq_fit_err:.0f}) [{fwhm*1e6:.1f} KHz]", "mode": "lines", "line":{"color":"black"}
        }

        data["text"] = {
            "x":[line_freq_fit-9e-5, line_freq_fit],
            "y":[half_max*.7, -2],
            "text":[f"{fwhm*1e6:.1f} KHz", f"{line_freq_fit:.7f} GHz"],
            "mode":"text", 
            "showlegend":False
        }

        data["shapes"] = {
                "center": {
                    "type":"line", "x0":line_freq_fit, "x1":line_freq_fit,
                    "y0": 0, "y1":amplitude,
                },
                "fwhm": {
                    "type":"line", "x0":line_freq_fit-fwhm/2, "x1":line_freq_fit+fwhm/2,
                    "y0": half_max, "y1":half_max
                }
            }

        dataToSend = json.dumps(data)
        print(dataToSend)

if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")

    filenames = [pt(i) for i in args[0:-3]]
    gamma = float(args[-1])*1e-3

    tkplot = args[-2]
    if tkplot == "plot": tkplot = True
    else: tkplot = False

    delta = float(args[-3]) # in Hz
    delta = delta*1e-9 # in GHz (to compare with our data)

    if tkplot:

        print(f"Received arguments: {args}")
        print(f"Received files: {filenames}")
        print(f"Gamma: {gamma} {args[-1]}")
        print(f"tkplot: {tkplot} {args[-2]}")
        print(f"Delta: {delta} {args[-3]}")

    main(filenames, delta, tkplot, gamma)