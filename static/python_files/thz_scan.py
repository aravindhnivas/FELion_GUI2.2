# Importing modules

# Data analysis
import numpy as np
from lmfit.models import GaussianModel

# Built-In modules
from pathlib import Path as pt
import sys, json

# FELion tkinter figure module
from FELion_widgets import FELion_Tk

def thz_plot(filename):
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

    # depletion_error = depletion.T.std(axis=1)*100

    depletion_counts = depletion_counts*100
    iteraton = int(resOn[0].shape[0]-1)
    steps = int(round((freq[1]-freq[0])*1e6, 0))

    return freq, depletion_counts, f"{steps} KHz : {iteraton} cycles"

def save_fig(filename, freq, depletion_counts, fit_data, line_freq_fit, amplitude, half_max, fwhm):

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
    #plt.show()
    plt.close()

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

def main(filenames, delta, tkplot):


    if len(filenames)>1: runavg = True
    else: runavg = False

    if tkplot:
        widget = FELion_Tk(title="Mass spectrum", location=filenames[0].parent)
        fig, canvas = widget.Figure()

        if len(filenames) == 1: savename=filenames[0].stem
        else: savename = "averaged_thzScan"

        ax = widget.make_figure_layout(title="THz scan", xaxis="Time (ms)", yaxis="counts", savename=savename)

    else: data = {}

    xs, ys = [], []

    for filename in filenames:

        filename = pt(filename)
        freq, depletion_counts, iteraton = thz_plot(filename)

        if tkplot:
            ax.plot(freq, depletion_counts, ".", label=f"{filename.name} [{iteraton}]")
        else:
            data[filename.name] = {"x": list(freq), "y": list(depletion_counts),  
                                    "name": f"{filename.name} [{iteraton}]", "mode":'markers',
                                    }

        xs = np.append(xs, freq)
        ys = np.append(ys, depletion_counts)

    if runavg: binx, biny = binning(xs, ys, delta)
    else: binx, biny = freq, depletion_counts

    model = GaussianModel()
    guess = model.guess(biny, x=binx)
    guess_values = guess.valuesdict()
    fit = model.fit(biny, x=binx, amplitude = guess_values['amplitude'], 
                    center = guess_values['center'], 
                    sigma = guess_values['sigma'], 
                    fwhm = guess_values['fwhm'], 
                    height = guess_values['height'])

    FWHM = lambda sigma: 2*np.sqrt(2*np.log(2))*sigma
    Amplitude = lambda a, sigma: a/(sigma*np.sqrt(2*np.pi))

    fit_data = fit.best_fit
    line_freq_fit = fit.best_values['center']
    sigma = fit.best_values['sigma']

    amplitude = Amplitude(fit.best_values['amplitude'], sigma)

    fwhm = FWHM(sigma)
    half_max = amplitude/2

    # Averaged

    if runavg:

        label = f"Averaged (delta={delta*1e6:.2f} KHz)"
        if tkplot: ax.plot(binx, biny, "k.", label=label)

        else:
            data["Averaged_exp"] = {
                "x": list(binx), "y": list(biny),  "name":label, "mode": "markers", "marker":{"color":"black"}
            }
    if tkplot:
        ax.plot(binx, fit_data, "k-", label=f"Fitted: {line_freq_fit:.7f} GHz ({fwhm*1e6:.1f} KHz)")
        ax.vlines(x=line_freq_fit, ymin=0, ymax=amplitude, zorder=10)
        ax.hlines(y=half_max, xmin=line_freq_fit-fwhm/2, xmax=line_freq_fit+fwhm/2, zorder=10)

        widget.plot_legend = ax.legend()
        widget.mainloop()
    else:

        data["Averaged_fit"] = {
            "x": list(binx), "y": list(fit_data),  "name": f"Fitted: {line_freq_fit:.7f} GHz ({fwhm*1e6:.1f} KHz)", "mode": "lines", "line":{"color":"black"}
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
    filenames = [pt(i) for i in args[0:-2]]
    delta = float(args[-2]) # in KHz

    delta = delta*1e-6 # in GHz (to compare with our data)

    tkplot = args[-1]
    if tkplot == "plot": tkplot = True
    else: tkplot = False

    if tkplot:
        print(f"delta: {delta} {args[-2]}")

    main(filenames, delta, tkplot)