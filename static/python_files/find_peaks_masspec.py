# Importing modules
import json, sys
from pathlib import Path as pt

# Data analysis
import numpy as np
from scipy.signal import find_peaks as peak

def find_mass_peaks(filename, prominence, width):

    mass, counts = np.genfromtxt(filename).T
    indices, _ = peak(counts, prominence=prominence, width=width)

    mass = list(mass[indices])
    counts = list(counts[indices])
    
    annotations = [

        {
            "x": x,
            "y": y,
            "xref": 'x',
            "yref": 'y',
            "text": f'{x:.2f}',
            "showarrow": True,
            "arrowhead": 2,
            "ax": -25,
            "ay": -40
        }
        
        for x, y in zip(mass, counts)
    ]

    dataToSend = {"annotations":annotations}
    dataJson = json.dumps(dataToSend)
    print(dataJson)

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")

    filename = pt(args[0])

    prominence = args[1]
    if prominence == "": prominence = None
    else: prominence = float(prominence)

    width = args[2]
    if width == "": width = None
    else: width = float(width)

    find_mass_peaks(filename, prominence, width)