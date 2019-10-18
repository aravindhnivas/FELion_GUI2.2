const {PythonShell} = require('python-shell')
const path = require('path')
const filename = "Y:/22pole_iontrap-exchange/Students/Aravindh/Measurements/CD+/masspec/30_08_19-9.mass"
const pythonPath = path.join(__dirname, "python3.7/python.exe")

pycode = `
from numpy import genfromtxt as openfile
from pathlib import Path as pt
import json
massfile = pt("${filename}")
mass, counts = openfile(massfile).T
data = json.dumps({"x":list(mass), "y":list(counts)})

print(data)
`
PythonShell.runString(pycode, { pythonPath: pythonPath }, function (err, data) {

    if (err) throw err;
    data = JSON.parse(data)
    console.log(data.x.length);
    
  });