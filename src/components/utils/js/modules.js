const { spawn } = require("child_process");
const path = require('path');
const fs = require("fs")

let screenWidth = window.screen.width
let plot_height = screenWidth * .22


function subplot(mainTitle, xtitle, ytitle, data, plotArea, x2, y2, data2) {

    let dataLayout = {
        title: mainTitle,
        xaxis: { domain: [0, 0.4], title: xtitle },
        yaxis: { title: ytitle },
        xaxis2: { domain: [0.5, 1], title: x2 },
        yaxis2: { anchor: "x2", title: y2, overlaying: 'y', },
        yaxis3: { anchor: 'free', overlaying: 'y', side: 'right', title: "Measured (mJ)", position: 0.97 },
        autosize: true,
        height: localStorage["plotly_height"],
        width: localStorage["plotly_width"]
    }

    let dataPlot1 = [];
    for (let x in data) { dataPlot1.push(data[x]) }
    let dataPlot2 = [];
    for (let x in data2) { dataPlot2.push(data2[x]) }
    Plotly.react(plotArea, dataPlot1.concat(dataPlot2), dataLayout, { editable: true })

}

function plot(mainTitle, xtitle, ytitle, data, plotArea, filetype = null) {

    let dataLayout = {
        title: mainTitle,
        xaxis: { title: xtitle},
        yaxis: {title: ytitle},
        hovermode: 'closest',
        autosize: true,
        height: localStorage["plotly_height"],
        width: localStorage["plotly_width"]
    }
    if (filetype == 'mass') { dataLayout.yaxis.type = "log" }
    else if (filetype == 'scan') { dataLayout.width = localStorage["plotly_width"] / 2 }

    let dataPlot = [];
    for (let x in data) { dataPlot.push(data[x]) }
    try { Plotly.react(plotArea, dataPlot, dataLayout, { editable: true }) } catch (err) { console.log("Error occured while plotting\n", err) }
}

class program {

    constructor(obj) {
        this.obj = obj
        console.log(":: constructor -> this.obj", this.obj);
        console.log(`Received ${obj.filetype}files:`, obj.files);
        this.filetype = obj.filetype
        this.mainbtn = obj.mainbtn;
        this.pyfile = obj.pyfile;
        this.files = obj.files
        this.args = obj.args
    }

    filecheck() {
        return new Promise((resolve, reject) => {
            if (this.files.length == 0) {
                reject("No files selected")
            } else { resolve(`Filecheck completed: ${this.filetype} files`) }
        })
    }

    run() {

        return new Promise((resolve, reject) => {
            if (this.filetype == "general") {
                let shell_value = document.getElementById(this.obj.filetag + "_shell").checked

                console.log("Sending general arguments: ", this.files.concat(this.args))
                const py = spawn(
                    localStorage["pythonpath"],
                    ["-i", path.join(localStorage["pythonscript"], this.pyfile), this.files.concat(this.args)],
                    {
                        detached: true,
                        stdio: 'ignore',
                        shell: shell_value
                    }
                );
                py.unref()
                resolve("Done");
            }
            else {

                let py;
                try {
                    py = spawn(
                        localStorage["pythonpath"],
                        [path.join(localStorage["pythonscript"], this.pyfile), this.files.concat(this.args)]
                    );
                } catch (err) { reject(`Check python location (Settings-->Configuration-->Pythonpath)\n${err}`) }

                py.stdout.on("data", data => {

                    console.log("Ouput from python")
                    let dataReceived = data.toString("utf8")
                    console.log(dataReceived)
                });

                let error_occured_py = false;

                let error_result;
                py.stderr.on("data", data => {
                    error_result = data
                    error_occured_py = true;
                });

                py.on("close", () => {
                    console.log("Returned to javascript");

                    if (!error_occured_py) {
                        try {
                            let dataFromPython = fs.readFileSync(path.join(localStorage["pythonscript"], "data.json"))
                            dataFromPython = JSON.parse(dataFromPython.toString("utf-8"))
                            console.log(dataFromPython)

                            if (this.filetype == "mass") {
                                
                                plot("Mass spectrum", "Mass [u]", "Counts", dataFromPython, "mplot", "mass");
    
                            } else if (this.filetype == "scan") {
                                
                                let filename = this.obj.plotArea.split("_t")[0]
                                plot(`Timescan Plot: ${filename}`, "Time (in ms)", "Counts", dataFromPython, this.obj.plotArea, "scan");
                            } else if (this.filetype == "felix") {

                                window.line = []
                                window.index = []
                                window.annotations = []
                                let normMethod = this.obj.normethod;
                                let delta = this.args[0];
    
                                let avgdataToPlot;
    
                                let signal_formula;
                                let ylabel;
    
                                if (normMethod === "Log") {
    
                                    avgdataToPlot = dataFromPython["average"]
    
                                    signal_formula = "Signal = -ln(C/B)/Power(in J)"
                                    ylabel = "Normalised Intensity per J"
    
                                } else if (normMethod == "Relative") {
    
                                    avgdataToPlot = dataFromPython["average_rel"]
    
                                    signal_formula = "Signal = (1-C/B)*100"
                                    ylabel = "Relative Depletion (%)"
    
                                } else if (normMethod == "IntensityPerPhoton") {
    
                                    avgdataToPlot = dataFromPython["average_per_photon"]
    
                                    signal_formula = "Signal = -ln(C/B)/#Photons"
                                    ylabel = "Normalised Intensity per photon"
                                }
    
    
                                const get_data = (data) => {
                                    let dataPlot = [];
                                    for (let x in data) { dataPlot.push(data[x]) }
                                    return dataPlot
                                }
                                let signal = {
                                    "rel": "Signal = (1-C/B)*100",
                                    "log": "Signal = -ln(C/B)/Power(in J)",
                                    "hv": "Signal = -ln(C/B)/#Photons"
                                }
                                const set_title = (method) => `Normalised and Averaged Spectrum (delta=${delta})<br>${signal[method]}; {C=Measured Count, B=Baseline Count}`
                                window.avg_data = {
                                    "Relative": {
                                        "data": get_data(dataFromPython["average_rel"]),
                                        "layout": {
                                            "title": set_title("rel"),
                                            "yaxis": { "title": "Relative Depletion (%)" },
                                            "xaxis": { "title": "Calibrated Wavelength (cm-1)" }
                                        }
                                    },
                                    "Log": {
                                        "data": get_data(dataFromPython["average"]),
                                        "layout": {
                                            "title": set_title("log"),
                                            "yaxis": { "title": "Normalised Intensity per J" },
                                            "xaxis": { "title": "Calibrated Wavelength (cm-1)" }
                                        }
                                    },
                                    "IntensityPerPhoton": {
                                        "data": get_data(dataFromPython["average_per_photon"]),
                                        "layout": {
                                            "title": set_title("hv"),
                                            "yaxis": { "title": "Normalised Intensity per photon" },
                                            "xaxis": { "title": "Calibrated Wavelength (cm-1)" }
                                        }
                                    },
    
                                }
    
                                plot(
                                    "Baseline Corrected",
                                    "Wavelength (cm-1)",
                                    "Counts",
                                    dataFromPython["base"],
                                    "bplot"
                                );
    
                                plot(
                                    `Normalised and Averaged Spectrum (delta=${delta})<br>${signal_formula}; {C=Measured Count, B=Baseline Count}`,
                                    "Calibrated Wavelength (cm-1)",
                                    ylabel,
                                    avgdataToPlot,
                                    "avgplot"
                                );
    
                                //Spectrum and Power Analyer
                                subplot(
                                    "Spectrum and Power Analyser",
                                    "Wavelength set (cm-1)",
                                    "SA (cm-1)",
                                    dataFromPython["SA"],
                                    "saPlot",
                                    "Wavelength (cm-1)",
                                    `Total Power (mJ)`,
                                    dataFromPython["pow"]
                                );
    
                                let avgplot = document.getElementById("avgplot")
                                avgplot.on("plotly_selected", (data) => {
                                    if (!data) console.log("No data available to fit")
                                    else {
                                        console.log(data)
    
                                        let { range } = data
                                        let filename = data.points[0].data.name.split(".")[0]
                                        window.index = range.x
                                        window.filename = filename
    
                                        console.log(`Selected file: ${window.filename}`)
                                        console.log(`Index selected: ${window.index}`)
                                        document.getElementById("fitFiles").value = filename
                                        document.getElementById("expfitFiles").value = filename
    
                                    }
                                })
                            } else if (this.filetype == "opofile") {
                                plot("OPO spectrum", "Wavenumber (cm-1)", "Counts", dataFromPython["real"], "opoplot");
                                plot("OPO spectrum: Depletion (%)", "Wavenumber (cm-1)", "Depletion (%)", dataFromPython["relative"], "opoRelPlot");
                            }
                            else if (this.filetype == "theory") {
    
                                let normethod = this.args[0];
                                let ylabel;
                                if (normethod === "Log") { ylabel = "Normalised Intensity per J" }
                                else if (normethod === "Relative") { ylabel = "Relative Depletion (%)" }
                                else { ylabel = "Normalised Intensity per Photon" }
    
                                let theoryData = [];
                                for (let x in dataFromPython["line_simulation"]) { theoryData.push(dataFromPython["line_simulation"][x]) }
    
                                plot(
                                    "Experimental vs Theory",
                                    "Calibrated Wavelength (cm-1)",
                                    ylabel, [dataFromPython["averaged"], ...theoryData],
                                    "exp-theory-plot"
                                );
                            }
                            else if (this.filetype == "thz") {
    
                                plot(`THz Scan`, "Frequency (GHz)", "Depletion (%)", dataFromPython, "thzplot_Container");
    
                                let lines = [];
    
                                for (let x in dataFromPython["shapes"]) { lines.push(dataFromPython["shapes"][x]) }
                                let layout_update = {
                                    shapes: lines
                                }
                                Plotly.relayout("thzplot_Container", layout_update)
                            }
                            else if (this.filetype == "boltzman") {
                                plot(`Boltzman Distribution`, "Rotational levels (J)", "Probability (%)", dataFromPython, "boltzman_plot");
                            }
                            // else if (this.filetype == "norm_tkplot") { console.log('Graph plotted') }
                            else if (this.filetype == "exp_fit") {
    
                                // window.index = []
    
                                Plotly.addTraces("avgplot", dataFromPython["fit"])
    
                                window.line = [...window.line, ...dataFromPython["line"]]
                                Plotly.relayout("avgplot", { shapes: window.line })
    
                                window.annotations = [...window.annotations, dataFromPython["annotations"]]
                                Plotly.relayout("avgplot", { annotations: window.annotations })
    
                            } else if (this.filetype == "expfit_all") {
                                Plotly.relayout("avgplot", { annotations: [] })
                                Plotly.relayout("avgplot", { annotations: dataFromPython[2]["annotations"] })
                                window.annotations = dataFromPython[2]["annotations"]
    
                                if (dataFromPython[3] != undefined) {
                                    let fit = dataFromPython[3]
                                    fit.forEach(data => {
                                        Plotly.addTraces("avgplot", data["fit"])
                                        window.line = [...window.line, ...data["line"]]
                                        Plotly.relayout("avgplot", { shapes: window.line })
    
                                    })
                                }
                            } else if (this.filetype == "find_peaks") {
                                Plotly.relayout("mplot", { yaxis: { title: "Counts", type: "" } })
                                Plotly.relayout("mplot", { annotations: [] })
                                Plotly.relayout("mplot", { annotations: dataFromPython["annotations"] })
                                Plotly.relayout("mplot", { yaxis: { title: "Counts", type: "log" } })
                            }
    
                            console.log("Graph Plotted");
    
                        } catch (err) {
                            console.error("Error Occured in javascript code: " + err);
                        }
                        resolve(`Plotted for ${this.filetype} file`)

                    } else {
                        reject(`Error Occured from python \n${error_result}\n`)
                    }

                });
            }
        })
    }
}

export { program }