const { spawn, exec } = require("child_process");
const path = require('path');
const pythonPath = path.join(__dirname, "../python3.7/python")
const functions_path = path.join(__dirname, "/python_files/")

const plot_width = window.screen.width * .625;
const plot_height = window.screen.height * .42;

// paper_bgcolor: '#c7c7c7',
// plot_bgcolor: '#c7c7c7'
function subplot(mainTitle, xtitle, ytitle, data, plotArea, x2, y2, data2) {
    let dataLayout = {

        title: mainTitle,

        xaxis: {
            domain: [0, 0.45],
            title: xtitle
        },
        yaxis: {
            title: ytitle
        },

        xaxis2: {
            domain: [0.5, 1],
            title: x2
        },
        yaxis2: {
            anchor: "x2",
            title: y2
        },

        autosize: true,
        width: plot_width,
        height: plot_height,
    };

    let dataPlot1 = [];
    for (let x in data) {
        dataPlot1.push(data[x]);
    }

    let dataPlot2 = [];
    for (let x in data2) {
        dataPlot2.push(data2[x]);
    }
    Plotly.react(plotArea, dataPlot1.concat(dataPlot2), dataLayout, { editable: true });
}

function plot(mainTitle, xtitle, ytitle, data, plotArea, filetype = null) {

    let dataLayout = {
        title: mainTitle,
        xaxis: {
            title: xtitle
        },
        yaxis: {
            title: ytitle
        },

        hovermode: 'closest',
        autosize: true,
        width: plot_width,
        height: plot_height,

    };

    if (filetype == 'mass') { dataLayout.yaxis.type = "log" }
    let dataPlot = [];
    for (let x in data) { dataPlot.push(data[x]) }

    try { Plotly.react(plotArea, dataPlot, dataLayout, { editable: true }) } catch (err) { console.log(err) }
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
    };

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
                let shell_value = document.getElementById(this.obj.filetag+"_shell").checked

                const py = spawn(
                    pythonPath, 
                    ["-i", path.join(functions_path, this.pyfile), this.files.concat(this.args)], 
                    {
                        detached: true,
                        stdio: 'ignore',
                        shell:shell_value
                    }
                );

                py.unref()

                resolve("Done");

            }
            else {

                const py = spawn(
                    pythonPath, 
                    [path.join(functions_path, this.pyfile), this.files.concat(this.args)]
                );

                
                py.stdout.on("data", data => {

                    let dataFromPython;
                    dataFromPython = data.toString("utf8");

                    // console.log("Before JSON parse :" + dataFromPython)

                    dataFromPython = JSON.parse(dataFromPython);
                    console.log("After JSON parse :", dataFromPython);

                    try {
                        if (this.filetype == "mass") {
                            plot("Mass spectrum", "Mass [u]", "Counts", dataFromPython, "mplot", "mass");
                        } else if (this.filetype == "scan") {
                            let filename = this.obj.plotArea.split("_t")[0]
                            plot(`Timescan Plot: ${filename}`, "Time (in ms)", "Counts", dataFromPython, this.obj.plotArea);
                        } else if (this.filetype == "felix") {

                            let normlog = this.obj.normethod;
                            let delta = this.args;

                            let felixdataToPlot;
                            let avgdataToPlot;

                            if (normlog) {

                                felixdataToPlot = dataFromPython["felix"];
                                avgdataToPlot = dataFromPython["average"]
                            } else {

                                felixdataToPlot = dataFromPython["felix_rel"]
                                avgdataToPlot = dataFromPython["average_rel"]
                            }

                            plot(
                                "Baseline Corrected",
                                "Wavelength (cm-1)",
                                "Intesity",
                                dataFromPython["base"],
                                "bplot"
                            );
                            let signal_formula;

                            normlog ? signal_formula = "Signal = -ln(C/B)/Power(in J)" : signal_formula = "Signal = (1-C/B)*100";

                            plot(
                                `Normalized Spectrum (delta=${delta})<br>${signal_formula}; {C=Measured Count, B=Baseline Count}`,
                                "Calibrated Wavelength (cm-1)",
                                normlog ? "Normalised Intesity" : "Relative depletion (%)",
                                felixdataToPlot,
                                "nplot"
                            );
                            plot(
                                `Average of Normalised Spectrum (delta=${delta})`,
                                "Calibrated Wavelength (cm-1)",
                                normlog ? "Normalised Intesity" : "Relative depletion (%)",
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
                                "Power (mJ)",
                                dataFromPython["pow"]
                            );

                        } else if (this.filetype == "theory") {

                            let log = this.args[0];
                            console.log(":: run -> log", log);

                            let theoryData = [];
                            for (let x in dataFromPython["line_simulation"]) { theoryData.push(dataFromPython["line_simulation"][x]) }

                            plot(
                                "Experimental vs Theory",
                                "Calibrated Wavelength (cm-1)",
                                log == "Log" ? "Normalised Intesity" : "Relative depletion (%)", [dataFromPython["averaged"], ...theoryData],
                                "exp-theory-plot"
                            );
                        } else if (this.filetype == "thz") {

                            
                            let delta_thz = this.args

                            plot(`THz Scan`, "Frequency (GHz)", "Depletion (%)", dataFromPython, "thzplot_Container");

                            let lines = [];

                            for (let x in dataFromPython["shapes"]) { lines.push(dataFromPython["shapes"][x]) }
                            let layout_update = {
                                shapes: lines
                            }
                            Plotly.relayout("thzplot_Container", layout_update)
                        }

                        console.log("Graph Plotted");

                    } catch (err) {
                        console.error("Error Occured in javascript code: " + err);
                    }

                });

                let error_occured_py = false;
                let error_result;

                py.stderr.on("data", data => {

                    error_result = data
                    error_occured_py = true;
                    // console.error(`Error from python: ${data}`);
                });

                py.on("close", () => {
                    console.log("Returned to javascript");

                    if (!error_occured_py) {
                        resolve(`Plotted for ${this.filetype} file`)

                    } else {
                        reject(`Error Occured from python \n${error_result}\n`)
                    }

                });
            }
        })
    }
}


exports.program = program