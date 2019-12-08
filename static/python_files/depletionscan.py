
# Built-In modules
import os, sys
from pathlib import Path as pt

# DATA analysis modules
import numpy as np
from scipy.optimize import curve_fit
from uncertainties import ufloat as uf, unumpy as unp

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

# FELion modules
from FELion_widgets import FELion_Tk
from timescan import timescanplot

class depletionplot:
    
    def __init__(self, location, resOnFile=None, resOffFile=None, power=None, nshots=10, massIndex=0, timeStart=1):

        self.location = pt(location)
        self.scanfiles = list(self.location.glob("*.scan"))
        self.resOnFile = resOnFile
        self.resOffFile = resOffFile

        self.power = {"resOn": power[0]/1000, "resOff": power[1]/1000} # mJ to J

        self.nshots = nshots
        self.massIndex = massIndex
        self.timeStart = timeStart
        self.widget = FELion_Tk(title="Depletion Plot", location=self.location)
        self.create_figure()
        self.startPlotting()

        self.widget.mainloop()
        
    def create_figure(self):
        
        self.fig, self.canvas = self.widget.Figure(default_widget=False)
        self.fig.suptitle("Depletion Scan")
        self.fig.subplots_adjust(top=0.86, bottom=0.14)
        self.ax0 = self.fig.add_subplot(121)
        self.ax1 = self.fig.add_subplot(122)

    def change_title(self, event): 
        
        self.fig.suptitle(self.widget.plotTitle.get())
        self.canvas.draw()

    def depletion_widgets(self, Koff, Kon, N, Na0, Nn0):

        # Position

        x0, x_diff = 0.1, 0.4
        y, y_diff = 0.16, 0.05

        # Row 1
        self.widget.plotTitle = self.widget.Entries("Entry", "Depletion Scan", x0, y, bind_key=True, bind_func=self.change_title, relwidth=0.7)

        # Row 2
        y += y_diff

        self.widget.koff_slider = self.widget.Sliders("Koff", Koff, x0, y, self.update, relwidth=0.5)
        self.widget.n_slider = self.widget.Sliders("N", N, x0, y+y_diff, self.update, relwidth=0.5)
        self.widget.kon_slider = self.widget.Sliders("Kon", Kon, x0, y+2*y_diff, self.update, relwidth=0.5)
        self.widget.na_slider = self.widget.Sliders("Na", Na0, x0, y+3*y_diff, self.update, relwidth=0.5)
        self.widget.nn_slider = self.widget.Sliders("Nn", Nn0, x0, y+4*y_diff, self.update, relwidth=0.5)

        # Row 3
        y += 6*y_diff

        self.widget.Labels("ON", x0, y)
        self.widget.Labels("OFF", x0+x_diff, y)

        # Row 4

        y += y_diff
        scanfiles_name = [name.name for name in self.scanfiles]

        self.widget.resOnList = self.widget.Dropdown(scanfiles_name, x0, y)
        self.widget.resOnList.set(self.resOnFile.name)
        
        self.widget.resOffList = self.widget.Dropdown(scanfiles_name, x0+x_diff, y)
        self.widget.resOffList.set(self.resOffFile.name)

        # Row 5
        y += y_diff

        self.new_power = self.widget.Entries("Entry", "21, 21", x0, y)
        self.new_nshots = self.widget.Entries("Entry", 10, x0+x_diff, y)

        # Row 6
        y += y_diff

        self.widget.Labels("MassIndex", x0, y)
        self.widget.Labels("TimeStartIndex", x0+x_diff, y)

        # Row 7
        y += y_diff

        self.new_massIndex = self.widget.Entries("Entry", self.massIndex, x0, y)
        self.new_timeStart = self.widget.Entries("Entry", self.timeStart, x0+x_diff, y)

        # Row 8
        y += y_diff

        self.submit = self.widget.Buttons("Replot", x0, y, self.replot)

    def replot(self):

        self.ax0.clear()
        self.ax1.clear()

        self.resOnFile = self.location / self.widget.resOnList.get()
        self.resOffFile = self.location / self.widget.resOffList.get()

        power = np.asarray(self.new_power.get().split(","), dtype=np.float)
        self.power = {"resOn": power[0]/1000, "resOff": power[1]/1000} # mJ to J

        self.nshots = self.new_nshots.get()
        self.massIndex = int(self.new_massIndex.get())
        self.timeStart = int(self.new_timeStart.get())

        print(f"ON: {self.resOnFile}\nOFF: {self.resOffFile}\nPower: {self.power}\nMassIndex: {self.massIndex}\nTimeStartIndex: {self.timeStart}")

        self.startPlotting(make_slider_widget=False)
        self.canvas.draw()

    def startPlotting(self, make_slider_widget=True):

        self.ax0.set(xlabel="n*t*E (mJ)", ylabel="Counts", title="Res ON-OFF scan")
        self.ax1.set(xlabel="n*t*E (mJ)", ylabel="Relative abundace of active isomer", title="$D(t)=A*(1-e^{-K_{ON}*(ntE)})$")
        for ax in (self.ax0, self.ax1): ax.grid()
        

        # Get timescan details
        self.get_timescan_data()

        # Fitt resOff and resOn
        Koff, N = self.resOff_fit()
        Na0, Nn0, Kon = self.resOn_fit(Koff, N)

        # if make_slider_widget: self.make_slider(Koff, Kon, N, Na0, Nn0)
        if make_slider_widget: self.depletion_widgets(Koff, Kon, N, Na0, Nn0)
        else:
            self.widget.koff_slider.set(Koff)
            self.widget.n_slider.set(N)
            self.widget.kon_slider.set(Kon)
            self.widget.na_slider.set(Na0)
            self.widget.nn_slider.set(Nn0)
        
        self.runFit(Koff, Kon, N, Na0, Nn0)

    def runFit(self, Koff, Kon, N, Na0, Nn0, plot=True):
        
        uKoff = uf(Koff, self.Koff_err)
        uN = uf(N, self.N_err)
        uNa0 = uf(Na0, self.Na0_err)
        uNn0 = uf(Nn0, self.Nn0_err)
        uKon = uf(Kon, self.Kon_err)

        lg1 = f"Kon: {uKon:.2uP}, Na: {uNa0:.2uP}, Nn: {uNn0:.2uP}"
        lg2 = f"Koff: {uKoff:.2uP}, N: {uN:.2uP}"

        self.ax0.legend(labels=[lg1, lg2], title=f"Mass: {self.mass[0]}u, Res: {self.t_res}V, B0: {self.t_b0}ms")

        self.get_depletion_fit(Koff, N, uKoff, uN, Na0, Nn0, Kon, uNa0, uNn0, uKon, plot)
        self.get_relative_abundance_fit(plot)

        self.ax1.legend(["Fitted", f"A: {self.uA:.3uP}", "Experiment"])

    
    def update(self, event):

        Koff = self.widget.koff_slider.get()
        Kon = self.widget.kon_slider.get()
        N = self.widget.n_slider.get()
        Na0 = self.widget.na_slider.get()
        Nn0 = self.widget.nn_slider.get()
        
        self.runFit(Koff, Kon, N, Na0, Nn0, plot=False)

        self.ax0_plot["resOn"].set_ydata(self.fitOn)
        self.ax0_plot["resOff"].set_ydata(self.fitOff)
        self.fit_plot.set_ydata(self.depletion_fitted)
        self.relativeFit_plot.set_ydata(self.relative_abundance)

        self.canvas.draw_idle()

    def get_timescan_data(self):

        self.data1 = {"resOn":{}, "resOff": {}}
        self.time = {"resOn":[], "resOff": []}
        self.counts = {"resOn":[], "resOff": []}
        self.error = {"resOn":[], "resOff": []}

        self.ax0_plot = {}
        for index, scanfile, i in zip(["resOn", "resOff"], [self.resOnFile, self.resOffFile], [0, 1]):

            time, counts, error, self.mass, self.t_res, self.t_b0 = timescanplot(scanfile).get_data()

            time = time/1000 # ms to s

            self.time[index] = np.array(time[self.timeStart:])
            self.counts[index] = np.array(counts[self.massIndex][self.timeStart:])
            self.error[index] = np.array(error[self.massIndex][self.timeStart:])

            self.power[index] = np.array((self.power[index] * self.nshots * self.time[index]))
            self.ax0.errorbar(self.power[index], self.counts[index], yerr=self.error[index], fmt=f"C{i}.")
        
    def N_OFF(self, x, K_OFF, N): return (N)*np.exp(-K_OFF*x)

    def resOff_fit(self, auto_plot=True):
        K_OFF_init = 0
        N_init = self.counts["resOff"].max()

        pop_off, popc_off = curve_fit(
            self.N_OFF, self.power["resOff"], self.counts["resOff"],
            sigma=self.error["resOff"],
            absolute_sigma=True,
            p0=[K_OFF_init, N_init],
            bounds=[(-np.inf, 0), (np.inf, N_init*2)]
        )

        perr_off = np.sqrt(np.diag(popc_off))
        Koff, N= pop_off
        self.Koff_err, self.N_err= perr_off     

        if auto_plot: return Koff, N
    
    def N_ON(self, x, Na0, Nn0, K_ON):
            K_OFF = self.Koff
            return Na0*np.exp(-K_ON*x)*np.exp(-K_OFF*x) + Nn0*np.exp(-K_OFF*x)

    def resOn_fit(self, Koff, N, auto_plot=True):

        self.Koff = Koff

        Na0_init, Nn0_init, K_ON_init = N, N/2, 0
        pop_on, popc_on = curve_fit(
            self.N_ON, self.power["resOn"], self.counts["resOn"],
            sigma=self.error["resOn"],
            absolute_sigma=True,
            p0=[Na0_init, Nn0_init, K_ON_init],
            bounds=[(0, 0, -np.inf), (N , N*2, np.inf)]
        )

        perr_on = np.sqrt(np.diag(popc_on))

        Na0, Nn0, Kon = pop_on
        self.Na0_err, self.Nn0_err, self.Kon_err = perr_on
        
        if auto_plot: return Na0, Nn0, Kon

    def uN_OFF(self, x, uN, uK_OFF): return uN*unp.exp(-uK_OFF*x)

    def uN_ON(self, x, uNa0, uNn0, uK_OFF, uK_ON): return uNa0 * \
        unp.exp(-uK_ON*x)*unp.exp(-uK_OFF*x) + uNn0*unp.exp(-uK_OFF*x)
        
    def get_depletion_fit(self, Koff, N, uKoff, uN, Na0, Nn0, Kon, uNa0, uNn0, uKon, plot=True):
        
        self.Kon = Kon
        self.Koff = Koff

        maxPower = np.append(self.power["resOn"], self.power["resOff"]).max()*2

        self.fitX = np.linspace(0, maxPower, 20)
        ufitX = unp.uarray(self.fitX, np.zeros(len(self.fitX)))

        self.fitOn = self.N_ON(self.fitX, Na0, Nn0, self.Kon)
        self.fitOff = self.N_OFF(self.fitX, Koff, N)

        self.fitOn_with_err = self.uN_ON(ufitX, uNa0, uNn0, uKoff, uKon)
        self.fitOff_with_err = self.uN_OFF(ufitX, uKoff, uN)
        
        self.fitted_counts_error = {"resOn": unp.std_devs(self.fitOn_with_err), "resOff": unp.std_devs(self.fitOff_with_err)}
        print(f"Exp counts error: {self.error}\nFitted counts error: {self.fitted_counts_error}\n")

        self.fitted_counts = {"resOn":np.array(self.fitOn), "resOff": np.array(self.fitOff)}
        print(f"Counts: {self.counts}\nFitted: {self.fitted_counts}\n")

        if plot:
            for index, fitY, i in zip(["resOn", "resOff"], [self.fitOn, self.fitOff], [0, 1]):
                self.ax0_plot[index], = self.ax0.plot(self.fitX, fitY, f"C{i}")

    def Depletion(self, x, A):
            K_ON = self.Kon
            return A*(1-np.exp(-K_ON*x))

    def get_relative_abundance_fit(self, plot=True):

        self.depletion_fitted = 1 - (self.fitted_counts["resOn"]/self.fitted_counts["resOff"])
        depletion_fitted_with_err = 1 - (unp.uarray(self.fitted_counts["resOn"], self.fitted_counts_error["resOn"])/unp.uarray(self.fitted_counts["resOff"], self.fitted_counts_error["resOff"]))
        self.depletion_fitted_err = unp.std_devs(depletion_fitted_with_err)

        self.depletion_exp = 1 - (self.counts["resOn"]/self.counts["resOff"])
        depletion_exp_with_err = 1 - (unp.uarray(self.counts["resOn"], self.error["resOn"])/unp.uarray(self.counts["resOff"], self.error["resOff"]))
        self.depletion_exp_err = unp.std_devs(depletion_exp_with_err)
        
        A_init = 0.5
        pop_depletion, popc_depletion = curve_fit(
            self.Depletion, self.fitX, self.depletion_fitted,
            sigma=self.depletion_fitted_err,
            absolute_sigma=True,
            p0=[A_init],
            bounds=[(0), (1)]
        )

        perr_depletion = np.sqrt(np.diag(popc_depletion))

        A = pop_depletion
        A_err = perr_depletion

        self.uA = uf(A, A_err)
        print(f"A: {self.uA:.3uP}")

        self.relative_abundance = self.Depletion(self.fitX, A)

        

        if plot:
            self.ax1.errorbar(self.power["resOn"], self.depletion_exp, yerr=self.depletion_exp_err, fmt="k.")
            self.fit_plot, = self.ax1.plot(self.fitX, self.depletion_fitted)
            self.relativeFit_plot, = self.ax1.plot(self.fitX, self.relative_abundance)
        
if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")

    location = args[0]

    resOnFile = pt(location)/args[1]
    resOffFile = pt(location)/args[2]
    power = np.asarray(args[3:5], dtype=np.float)
    nshots = int(args[5])
    
    massIndex = int(args[6])
    TimeIndex = int(args[7])

    print(f'Location: {location}\nON: {resOnFile}\nOFF: {resOffFile}\npower: {power} {type(power)}\nshots: {nshots} {type(nshots)}')
    print(f"MassIndex: {massIndex}\nTimeIndex: {TimeIndex}")

    depletionplot(location, resOnFile, resOffFile, power, nshots, massIndex, TimeIndex)