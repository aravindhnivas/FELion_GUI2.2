
import os, sys
from pathlib import Path as pt
from FELion_definitions import delete_last_line

if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")

    filename = f"{args[0]}.expfit"
    location = pt(args[1])
    if location.name is "DATA": datfile_location = location.parent/"EXPORT"
    else: datfile_location = location/"EXPORT"

    filename = datfile_location / filename
    delete_last_line(filename)