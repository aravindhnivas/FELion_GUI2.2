# Importing Modules

# System modules
import sys
import json
import os
import shutil
from os.path import isdir, isfile, dirname
from pathlib import Path as pt
from itertools import cycle

# Data analysis
import numpy as np
from scipy.interpolate import interp1d

# FELion modules
from FELion_baseline_old import felix_read_file, BaselineCalibrator
from FELion_power import PowerCalibrator
from FELion_sa import SpectrumAnalyserCalibrator
from baseline import Create_Baseline

######################################################################################

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

def var_find(openfile):

    var = {'res': 'm03_ao13_reso', 'b0': 'm03_ao09_width',
           'trap': 'm04_ao04_sa_delay'}
    with open(openfile, 'r') as mfile:
        mfile = np.array(mfile.readlines())

    for line in mfile:
        if not len(line.strip()) == 0 and line.split()[0] == '#':
            for j in var:
                if var[j] in line.split():
                    var[j] = float(line.split()[-3])

    res, b0, trap = round(var['res'], 2), int(
        var['b0']/1000), int(var['trap']/1000)

    return res, b0, trap

class normplot:
    def __init__(self, received_files, delta, felix_hz=10):

        self.delta = delta
        received_files = [pt(files) for files in received_files]

        location = received_files[0].parent

        back_dir = dirname(location)
        folders = ["DATA", "EXPORT", "OUT"]
        if set(folders).issubset(os.listdir(back_dir)): 
            self.location = pt(back_dir)
        else: 
            self.location = pt(location)

        os.chdir(self.location)

        dataToSend = {"felix": {}, "base": {}, "average": {}, "SA": {}, "pow": {}, "felix_rel": {}, "average_rel": {}}

        # For Average binning (Norm. method: log)
        xs = np.array([], dtype=np.float)
        ys = np.array([], dtype=np.float)

        # For Average binning (Norm. method: rel)
        xs_r = np.array([], dtype=np.float)
        ys_r = np.array([], dtype=np.float)

        # FELIX Hz
        self.felix_hz = felix_hz

        c = 0
        group = 1

        for filename in received_files:

            res, b0, trap = var_find(filename)
            label = f"Res:{res}; B0: {b0}ms; trap: {trap}ms"
            self.nshots = (trap/1000) * self.felix_hz

            felixfile = filename.name
            fname = filename.stem
            basefile = f"{fname}.base"
            powerfile = f"{fname}.pow"

            self.filetypes = [felixfile, basefile, powerfile]

            for folder, filetype in zip(folders, self.filetypes):
                if not isdir(folder):
                    os.mkdir(folder)
                if isfile(filetype):
                    shutil.move(
                        self.location.joinpath(filetype),
                        self.location.joinpath("DATA", filetype),
                    )

            # Wavelength and intensity of individuals without binning
            wavelength, intensity, raw_intensity, relative_depletion = self.norm_line_felix()
            wavelength_rel = np.copy(wavelength)

            # collecting Wavelength and intensity to average spectrum with binning
            xs = np.append(xs, wavelength)
            ys = np.append(ys, intensity)

            xs_r = np.append(xs_r, wavelength_rel)
            ys_r = np.append(ys_r, relative_depletion)

            # Wavelength and intensity of individuals with binning
            wavelength, intensity = self.felix_binning(
                wavelength, intensity)

            wavelength_rel, relative_depletion = self.felix_binning(
                wavelength_rel, relative_depletion)

            # self.powerPlot(powerfile, wavelength)
            ##################################

            # Spectrum Analyser

            wn, sa = self.saCal.get_data()
            X = np.arange(wn.min(), wn.max(), 1)
            
            dataToSend["SA"][felixfile] = {
                "x": list(wn),
                "y": list(sa),
                "name": f"{filename.stem}_SA",
                "mode": "markers",
                "line": {"color": f"rgb{colors[c]}"},
                "legendgroup": f'group{group}',
            }

            dataToSend["SA"][f"{felixfile}_fit"] = {
                "x": list(X),
                "y": list(self.saCal.sa_cm(X)),
                "name": f"{filename.stem}_fit",
                "type": "scatter",
                "line": {"color": "black"},
                "showlegend": False,
                "legendgroup": f'group{group}',
            }
            
            ###############################

            dataToSend["felix"][f"{felixfile}_histo"] = {
                "x": list(wavelength),
                "y": list(intensity),
                "name": felixfile,
                "type": "bar",
                "marker": {"color": f"rgb{colors[c]}"},
                "legendgroup": 'group',
            }

            dataToSend["felix"][felixfile] = {
                "x": list(wavelength),
                "y": list(intensity),
                "name": felixfile,
                "type": "scatter",
                "line": {"color": f"rgb{colors[c]}"},
            }


            dataToSend["felix_rel"][f"{felixfile}_histo"] = {
                "x": list(wavelength_rel),
                "y": list(relative_depletion),
                "name": felixfile,
                "type": "bar",
                "marker": {"color": f"rgb{colors[c]}"},
                "legendgroup": 'group',
            }

            dataToSend["felix_rel"][felixfile] = {
                "x": list(wavelength_rel),
                "y": list(relative_depletion),
                "name": felixfile,
                "type": "scatter",
                "line": {"color": f"rgb{colors[c]}"},
            }


            dataToSend["average"][felixfile] = {
                "x": list(wavelength),
                "y": list(intensity),
                "name": felixfile,
                "mode": "markers",
                "line": {"color": f"rgb{colors[c]}"},
            }

            dataToSend["average_rel"][felixfile] = {
                "x": list(wavelength_rel),
                "y": list(relative_depletion),
                "name": felixfile,
                "mode": "markers",
                "line": {"color": f"rgb{colors[c]}"},
            }

            self.export_file(fname, wavelength, intensity, raw_intensity, relative_depletion)

            basefile_data = np.array(
                Create_Baseline(felixfile, self.location,
                                plotIt=False, checkdir=False, verbose=False).get_data()
            )

            # Ascending order sort by wn
            base_line = basefile_data[1][0]
            base_line = np.take(
                base_line, base_line[0].argsort(), 1).tolist()
            base_felix = basefile_data[0]
            base_felix = np.take(
                base_felix, base_felix[0].argsort(), 1).tolist()

            dataToSend["base"][f"{felixfile}_base"] = {
                "x": list(base_felix[0]),
                "y": list(base_felix[1]),
                "name": f"{felixfile}: {label}",
                "mode": "lines",
                "line": {"color": f"rgb{colors[c]}"},
                "legendgroup": f'group{group}'
            }

            dataToSend["base"][f"{felixfile}_line"] = {
                "x": list(base_line[0]),
                "y": list(base_line[1]),
                "name": f"{filename.stem}_base",
                "mode": "lines+markers",
                "marker": {"color": "black"},
                "legendgroup": f'group{group}',
                "showlegend": False,
            }

            dataToSend["pow"][powerfile] = {
                "x": list(wavelength),
                "y": list(self.total_power),
                "name": f"{powerfile}: [{self.nshots}]",
                "mode": "markers",
                "xaxis": "x2",
                "yaxis": "y2",
                "marker": {"color": f"rgb{colors[c]}"},
                "legendgroup": f'group{group}',
                "showlegend": True,
            }

            group += 1
            c += 2

        binns, intens = self.felix_binning(xs, ys)
        self.export_file("averaged_Log", binns, intens)

        dataToSend["average"]["average"] = {
            "x": list(binns),
            "y": list(intens),
            "name": "Averaged",
            "mode": "lines",
            "line": {"color": "black"},
        }

        # For relative
        binns_r, intens_r = self.felix_binning(xs_r, ys_r)
        self.export_file("averaged_Relative", binns_r, intens_r)
        
        dataToSend["average_rel"]["average"] = {
            "x": list(binns_r),
            "y": list(intens_r),
            "name": "Averaged",
            "mode": "lines",
            "line": {"color": "black"},
        }

        # print(f"Before JSON DATA: {dataToSend}")
        dataJson = json.dumps(dataToSend)
        print(dataJson)
        # print("DONE")

    def norm_line_felix(self, PD=True):

        felixfile, basefile, powerfile = self.filetypes

        data = felix_read_file(felixfile)
        powCal = PowerCalibrator(powerfile)
        baseCal = BaselineCalibrator(basefile)
        self.saCal = SpectrumAnalyserCalibrator(felixfile)

        wavelength = self.saCal.sa_cm(data[0])

        # self.nshots = powCal.shots(1.0)
        # self.total_power = powCal.power(data[0])*powCal.shots(data[0])
        self.power_measured = powCal.power(data[0])
        self.total_power = self.power_measured*self.nshots
        counts = data[1]
        baseCounts = baseCal.val(data[0])
        ratio = counts/baseCounts
        
        # Normalise the intensity
        # multiply by 1000 because of mJ but ONLY FOR PD!!!
        if PD:
            intensity = (-np.log(ratio)/self.total_power)*1000
        else:
            intensity = (baseCounts-counts)/self.total_power
        
        relative_depletion =(1-ratio)*100
        # relative_depletion = (baseCounts-counts)/total_power # For power normalising

        return wavelength, intensity, data[1], relative_depletion

    def export_file(self, fname, wn, inten, raw_intensity=None, relative_depletion=None):

        f = open('EXPORT/' + fname + '.dat', 'w')
        if raw_intensity is not None:
            f.write("#NormalisedWavelength(cm-1)\t#NormalisedIntensity\t#RawIntensity\t#RelativeDepletion(%)\n")
            for i in range(len(wn)):
                f.write(f"{wn[i]}\t{inten[i]}\t{raw_intensity[i]}\t{relative_depletion[i]}\n")
        else:
            f.write("#NormalisedWavelength(cm-1)\t#AveragedIntensity\n")
            for i in range(len(wn)):
                f.write(f"{wn[i]}\t{inten[i]}\n")

        f.close()


    def felix_binning(self, xs, ys):

        delta = self.delta
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

        return binsx, data_binned

    def powerPlot(self, powerfile, wavelength):
        # with open(f"./DATA/{powerfile}") as f:
        #     for line in f:
        #         if line[0] == "#":
        #             if line.find("SHOTS") == 1:
        #                 self.n_shots = float(line.split("=")[-1])

        # self.xw, self.yw = np.genfromtxt(f"./DATA/{powerfile}").T
        # self.f = interp1d(self.xw, self.yw, kind="linear",
        #                   fill_value="extrapolate")
        self.power_wn = wavelength
        self.power_mj = self.total_power

        # self.power_mj = self.f(wavelength)

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    filepaths = args[:-1]
    delta = float(args[-1])
    normplot(filepaths, delta)