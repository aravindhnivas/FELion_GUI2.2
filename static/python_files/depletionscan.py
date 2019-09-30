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

# Plotly module for graphing
from plotly import graph_objects as go
from plotly.offline import plot

# Dash
import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
import dash_daq as daq

class depletionplot:
    
    def __init__(self, resOnFile=None, resOffFile=None, power=None, nshots=10, massIndex=0, timeStart=1):

        self.resOnFile = resOnFile
        self.resOffFile = resOffFile

        self.power = {"resOn": power[0]/1000, "resOff": power[1]/1000} # mJ to J
        self.nshots = nshots
        self.massIndex = massIndex
        self.timeStart = timeStart
        self.app = dash.Dash(__name__)
        self.plotAll()

    def get_timescan_data(self):

        self.data1 = {"resOn":{}, "resOff": {}}
        self.time = {"resOn":[], "resOff": []}
        self.counts = {"resOn":[], "resOff": []}
        self.error = {"resOn":[], "resOff": []}

        for index, scanfile in zip(["resOn", "resOff"], [self.resOnFile, self.resOffFile]):

            time, counts, error, mass, t_res, t_b0 = timescanplot(scanfile).get_data()
            time = time/1000 # ms to s

            self.time[index] = np.array(time[self.timeStart:])
            self.counts[index] = np.array(counts[self.massIndex][self.timeStart:])
            self.error[index] = np.array(error[self.massIndex][self.timeStart:])

            self.power[index] = np.array((self.power[index] * self.nshots * self.time[index]))

            self.data1[index] = {
                "x": self.power[index],
                "y": self.counts[index],
                "name": f"[{index}]\n{mass}u, B0: {t_b0}ms, Res:{t_res}",
                "mode":'markers',
                "error_y": {
                    "type":"data",
                    "array": self.error[index],
                    "visible":True
                },
                "marker":{"color":"black"}
            }

        self.trace1 = [self.data1["resOn"], self.data1["resOff"]]
        print(f"Time: {self.time}\nPower: {self.power}")
  
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

        data2 = {"resOn":{}, "resOff":{}}
        legends = [f"Na0: {uNa0:.3uP}, Nn0: {uNn0:.3uP}, K_on: {uKon:.3uP}", f"N: {uN:.3uP}, K_off: {uKoff:.3uP}"]

        for index, fitY, name in zip(["resOn", "resOff"], [fitOn, fitOff], legends):
            data2[index] = {
                    "x": self.fitX,
                    "y": fitY,
                    "name": f"fit[{index}]: {name}",
                    "mode":'lines+markers',
                    }

        self.trace2 = [data2["resOn"], data2["resOff"]]

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
        
        data3 = {}

        data3["fromExpFit"] = {
            "x": self.fitX,
            "y": depletion_fitted,
            "name": "fromExpFit",
            "mode":'lines+markers',
            "xaxis": "x2",
            "yaxis": "y2",
            "error_y": {
                    "type":"data",
                    "array": depletion_fitted_err,
                    "visible":True
                },
        }

        data3["fromExp"] = {
            "x": self.power["resOn"],
            "y": depletion_exp,
            "name": "fromExp",
            "mode":'markers',
            "xaxis": "x2",
            "yaxis": "y2",
            "error_y": {
                    "type":"data",
                    "array": depletion_exp_err,
                    "visible":True
                },
            "marker":{"color":"black"}
        }

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

        data3["realtive_abundance_fit"] = {
            "x": self.fitX,
            "y": relative_abundance,
            "name": f"Fitted: A: {uA*100:.3uP}%",
            "mode":'lines+markers',
            "xaxis": "x2",
            "yaxis": "y2",
        }

        print(f"A: {uA:.3uP}")

        self.trace3 = [data3["fromExp"], data3["fromExpFit"], data3["realtive_abundance_fit"]]
    
    def plotAll(self):

        self.get_timescan_data()

        Koff, N = self.resOff_fit()
        Na0, Nn0, Kon = self.resOn_fit(Koff, N)

        uKoff = uf(Koff, self.Koff_err)
        uN = uf(N, self.N_err)
        uNa0 = uf(Na0, self.Na0_err)
        uNn0 = uf(Nn0, self.Nn0_err)
        uKon = uf(Kon, self.Kon_err)

        self.get_depletion_fit(Koff, N, uKoff, uN, Na0, Nn0, Kon, uNa0, uNn0, uKon)
        self.get_relative_abundance_fit()

        traces = self.trace1 + self.trace2 + self.trace3

        layout = {
            'height': 750,
            'margin': {
                'l': 10, 'b': 20, 't': 30, 'r': 0
            },
            "xaxis": {
                "domain":[0, 0.45],
                "title": "Power (J) [n*t*E]"
            },
            "yaxis": {
                "title": "Counts"
            },

            "xaxis2":{
                "domain":[0.5, 1],
                "title": "Power (J) [n*t*E]"
            },

            "yaxis2":{
                "anchor":"x2",
                "title": "Relative abundance of active isomer"
            }
        }
        
        Koff_dict = {f'{Koff}':f'{Koff:.2f}'}
        Kon_dict = {f'{Kon}':f'{Kon:.2f}'}
        N_dict = {f'{N}':f'{N:.2f}'}
        Na0_dict = {f'{Na0}':f'{Na0:.2f}'}
        Nn0_dict = {f'{Nn0}':f'{Nn0:.2f}'}

        for i in range(3, 10, 2):
            Koff_dict[f'{Koff*i}'] = f'{Koff*i:.2f}'
            Kon_dict[f'{Kon*i}'] = f'{Kon*i:.2f}'
            N_dict[f'{N*i}'] = f'{int(N*i)}'
            Na0_dict[f'{Na0*i}'] = f'{int(Na0*i)}'
            Nn0_dict[f'{Nn0*i}'] = f'{int(Nn0*i)}'

        sliders1 = [
            daq.Slider(
                id='Koff_slider',
                min=0,
                max=Koff*10,
                value=Koff,
                step=Koff/10,
                marks=Koff_dict
            ),

            daq.Slider(
                id='N_slider',
                min=0,
                max=N*10,
                value=N,
                step=100,
                marks=N_dict
            )
        ]

        sliders2 = [
             daq.Slider(
                id='Kon_slider',
                min=0,
                max=Kon*10,
                value=Kon,
                step=Kon/10,
                marks=Kon_dict
            ),

             daq.Slider(
                id='Na0_slider',
                min=0,
                max=Na0*10,
                value=Na0,
                step=100,
                marks=Na0_dict
            ),

             daq.Slider(
                id='Nn0_slider',
                min=0,
                max=Nn0*10,
                value=Nn0,
                step=100,
                marks=Nn0_dict
            ),
        ]

        graph = dcc.Graph(
                id='plot',
                figure={
                    'data': traces,
                    'layout': layout
                    }
                )
        

        self.app.layout = html.Div(className = 'container-fluid', children=[

            html.Div(className='row', children=[
                html.Div(className='column', children=[html.H2("Depletion Plot"), graph])
            ]),

            html.Div(className='row', children=[
                html.Div(className='six columns', style={"padding-top":"1em"}, children=[

                    html.Ul(className='flex-row', children=[
                        html.Li(style={"padding-top":"0.4em"}, children=sliders1[0]),
                        html.Li(style={"padding-left":"1em"}, children=html.Label('Koff'))
                    ]),

                    html.Ul(className='flex-row', children=[
                        html.Li(style={"padding-top":"0.4em"}, children=sliders1[1]),
                        html.Li(style={"padding-left":"1em"}, children=html.Label('N'))
                    ]),

                ]),

                html.Div(className='six columns', style={"padding-top":"1em"}, children=[

                    html.Ul(className='flex-row', children=[
                        html.Li(style={"padding-top":"0.4em"}, children=sliders2[0]),
                        html.Li(style={"padding-left":"1em"}, children=html.Label('Kon'))
                    ]),

                    html.Ul(className='flex-row', children=[
                        html.Li(style={"padding-top":"0.4em"}, children=sliders2[1]),
                        html.Li(style={"padding-left":"1em"}, children=html.Label('Na0'))
                    ]),

                    html.Ul(className='flex-row', children=[
                        html.Li(style={"padding-top":"0.4em"}, children=sliders2[2]),
                        html.Li(style={"padding-left":"1em"}, children=html.Label('Nn0'))
                    ]),

                ]),
            ]),
        ])

        @self.app.callback(
            Output('plot', 'figure'),
            [
                Input('Koff_slider', 'value'),
                Input('N_slider', 'value'),
                Input('Kon_slider', 'value'),
                Input('Na0_slider', 'value'),
                Input('Nn0_slider', 'value')
            ]
        )
        def update_figure(Koff, N, Kon, Na0, Nn0):

            uKoff = uf(Koff, self.Koff_err)
            uN = uf(N, self.N_err)
            uNa0 = uf(Na0, self.Na0_err)
            uNn0 = uf(Nn0, self.Nn0_err)
            uKon = uf(Kon, self.Kon_err)

            self.get_depletion_fit(Koff, N, uKoff, uN, Na0, Nn0, Kon, uNa0, uNn0, uKon)
            self.get_relative_abundance_fit()
            traces = self.trace1 + self.trace2 + self.trace3

            fig = go.Figure(traces, layout)
            fig.update_layout(legend_orientation="h")
            return fig
        
        
        self.app.run_server(port=5000, debug=True)

        print("Done")
        
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

    depletionplot(resOnFile, resOffFile, power, nshots, massIndex, TimeIndex)