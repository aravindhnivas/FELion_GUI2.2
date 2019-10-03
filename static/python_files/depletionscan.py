from timescan import timescanplot

# DATA analysis modules
import numpy as np
from scipy.optimize import curve_fit
from uncertainties import ufloat as uf
from uncertainties import unumpy as unp

# Built-In modules
import os
import sys
from pathlib import Path as pt

# Matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

class depletionplot:
    
    def __init__(self, resOnFile=None, resOffFile=None, power=None, nshots=10, massIndex=0, timeStart=1):

        self.resOnFile = resOnFile
        self.resOffFile = resOffFile

        self.power = {"resOn": power[0]/1000, "resOff": power[1]/1000} # mJ to J
        self.nshots = nshots
        self.massIndex = massIndex
        self.timeStart = timeStart

        self.fig, (self.ax0, self.ax1) = plt.subplots(nrows=1, ncols=2)
        self.canvas = self.fig.canvas
        self.fig.suptitle("Depletion scan")

        self.ax0.set(xlabel="n*t*E (mJ)", ylabel="Counts", title=f"resON[{power[0]}mJ]: {resOnFile.name}, resOFF[{power[1]}mJ]: {resOffFile.name}")

        self.ax1.set(xlabel="n*t*E (mJ)", ylabel="Relative abundace of active isomer", title="$D(t)=A*(1-e^{-K_{ON}*(ntE)})$")

        self.get_timescan_data()

        Koff, N = self.resOff_fit()
        Na0, Nn0, Kon = self.resOn_fit(Koff, N)

        uKoff = uf(Koff, self.Koff_err)
        uN = uf(N, self.N_err)
        uNa0 = uf(Na0, self.Na0_err)
        uNn0 = uf(Nn0, self.Nn0_err)
        uKon = uf(Kon, self.Kon_err)

        lg1 = f"Kon: {uKon:.2uP}, Na: {uNa0:.2uP}, Nn: {uNn0:.2uP}"
        lg2 = f"Koff: {uKoff:.2uP}, N: {uN:.2uP}"
        self.ax0.legend(labels=[lg1, lg2], title=f"Mass: {self.mass[0]}u, Res: {self.t_res}V, B0: {self.t_b0}ms")


        self.get_depletion_fit(Koff, N, uKoff, uN, Na0, Nn0, Kon, uNa0, uNn0, uKon)
        self.get_relative_abundance_fit()

        self.ax1.legend()
        for ax in (self.ax0, self.ax1): ax.grid()

        # controlling fitting parameters
        axcolor = 'lightgoldenrodyellow'

        l = 0.1
        koff_g = self.fig.add_axes([l, 0.12, 0.2, 0.015], facecolor=axcolor) # [left, bottom, width, height]
        n_g = self.fig.add_axes([l, 0.10, 0.2, 0.015], facecolor=axcolor)
        kon_g = self.fig.add_axes([l, 0.08, 0.2, 0.015], facecolor=axcolor)
        na_g = self.fig.add_axes([l, 0.06, 0.2, 0.015], facecolor=axcolor)
        nn_g = self.fig.add_axes([l, 0.04, 0.2, 0.015], facecolor=axcolor)

        self.koff_slider = Slider(koff_g, '$K_{OFF}$', 0, Koff*10, valinit=Koff)
        self.n_slider = Slider(n_g, 'N', 0, N*10, valinit=N)
        self.kon_slider = Slider(kon_g, '$K_{ON}$', 0, Kon*10, valinit=Kon)
        self.na_slider = Slider(na_g, '$Na_0$', 0, 10*Na0, valinit=Na0)
        self.nn_slider = Slider(nn_g, '$Nn_0$', 0, 10*Nn0, valinit=Nn0)


        self.koff_slider.on_changed(self.update)
        self.n_slider.on_changed(self.update)
        self.kon_slider.on_changed(self.update)
        self.na_slider.on_changed(self.update)
        self.nn_slider.on_changed(self.update)

        plt.subplots_adjust(top=0.92, bottom=0.2)
        plt.show()

    def update(self):
        pass

    def get_timescan_data(self):

        self.data1 = {"resOn":{}, "resOff": {}}
        self.time = {"resOn":[], "resOff": []}
        self.counts = {"resOn":[], "resOff": []}
        self.error = {"resOn":[], "resOff": []}

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
        
    def get_depletion_fit(self, Koff, N, uKoff, uN, Na0, Nn0, Kon, uNa0, uNn0, uKon):
        
        self.Kon = Kon
        self.Koff = Koff

        maxPower = np.append(self.power["resOn"], self.power["resOff"]).max()*2

        self.fitX = np.linspace(0, maxPower, 20)
        ufitX = unp.uarray(self.fitX, np.zeros(len(self.fitX)))

        fitOn = self.N_ON(self.fitX, Na0, Nn0, self.Kon)
        fitOff = self.N_OFF(self.fitX, Koff, N)

        fitOn_with_err = self.uN_ON(ufitX, uNa0, uNn0, uKoff, uKon)
        fitOff_with_err = self.uN_OFF(ufitX, uKoff, uN)
        
        self.fitted_counts_error = {"resOn": unp.std_devs(fitOn_with_err), "resOff": unp.std_devs(fitOff_with_err)}
        print(f"Exp counts error: {self.error}\nFitted counts error: {self.fitted_counts_error}\n")

        self.fitted_counts = {"resOn":np.array(fitOn), "resOff": np.array(fitOff)}
        print(f"Counts: {self.counts}\nFitted: {self.fitted_counts}\n")

        for fitY, i in zip([fitOn, fitOff], [0, 1]):
            self.ax0.plot(self.fitX, fitY, f"C{i}")

    def Depletion(self, x, A):
            K_ON = self.Kon
            return A*(1-np.exp(-K_ON*x))

    def get_relative_abundance_fit(self):

        depletion_fitted = 1 - (self.fitted_counts["resOn"]/self.fitted_counts["resOff"])
        depletion_fitted_with_err = 1 - (unp.uarray(self.fitted_counts["resOn"], self.fitted_counts_error["resOn"])/unp.uarray(self.fitted_counts["resOff"], self.fitted_counts_error["resOff"]))
        depletion_fitted_err = unp.std_devs(depletion_fitted_with_err)

        depletion_exp = 1 - (self.counts["resOn"]/self.counts["resOff"])
        depletion_exp_with_err = 1 - (unp.uarray(self.counts["resOn"], self.error["resOn"])/unp.uarray(self.counts["resOff"], self.error["resOff"]))
        depletion_exp_err = unp.std_devs(depletion_exp_with_err)
        

        self.ax1.errorbar(self.fitX, depletion_fitted, yerr=depletion_fitted_err, label=f"Fitted")
        self.ax1.errorbar(self.power["resOn"], depletion_exp, yerr=depletion_exp_err, fmt="k.", label="Experiment")


        A_init = 0.5
        pop_depletion, popc_depletion = curve_fit(
            self.Depletion, self.fitX, depletion_fitted,
            sigma=depletion_fitted_err,
            absolute_sigma=True,
            p0=[A_init],
            bounds=[(0), (1)]
        )
        perr_depletion = np.sqrt(np.diag(popc_depletion))

        A = pop_depletion
        A_err = perr_depletion
        uA = uf(A, A_err)

        relative_abundance = self.Depletion(self.fitX, A)
        self.ax1.plot(self.fitX, relative_abundance, label=f"A: {uA:.3uP}")
        print(f"A: {uA:.3uP}")
        
if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    # print(args)

    location = args[0]

    resOnFile = pt(location)/args[1]
    resOffFile = pt(location)/args[2]
    power = np.asarray(args[3:5], dtype=np.float)
    nshots = int(args[5])
    
    massIndex = int(args[6])
    TimeIndex = int(args[7])

    print(f'Location: {location}\nON: {resOnFile}\nOFF: {resOffFile}\npower: {power} {type(power)}\nshots: {nshots} {type(nshots)}')
    print(f"MassIndex: {massIndex}\nTimeIndex: {TimeIndex}")

    depletionplot(resOnFile, resOffFile, power, nshots, massIndex, TimeIndex)