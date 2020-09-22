#!/usr/bin/env python3

import os
import subprocess
import sys

# build directory needs to have BUILD_FORTRAN configured ON so ReadVars can be executed
BuildDir = '/eplus/repos/4eplus/builds/r'
ProductsDir = '/eplus/repos/4eplus/builds/r/Products'
FileToRun = '/tmp/test_for_julien.idf'
EioLineMatch = 'PACKAGED ROOFTOP AIR CONDITIONER, Cooling, Sensible'
EioTokenColumnIndex = 4

"""
(IOFreeze) "GOOD": 17861.42,
(RC2) "BAD": 21931.77
"""


def is_value_good(value) -> bool:
    """Returns true if the value is "good", and false if not"""
    float_value = float(value)
    return float_value < 19000


print('*** Attempting to build EnergyPlus')
try:
    subprocess.check_call(['make', '-j', '4', 'energyplus'], cwd=BuildDir)
except subprocess.CalledProcessError:
    print('*** An error occurred trying to build EnergyPlus -- returning 125 to skip this commit')
    sys.exit(125)

print('*** Running EnergyPlus with ReadVars and gathering output')
try:
    subprocess.check_call(['./energyplus', '-D', FileToRun], cwd=ProductsDir)
    eio_path = os.path.join(ProductsDir, 'eplusout.eio')
    with open(eio_path) as eio:
        for line in eio.readlines():
            if EioLineMatch in line:
                line_tokens = line.split(',')
                token = line_tokens[EioTokenColumnIndex]
                is_it_good = is_value_good(token)
                if is_it_good:
                    print("Match is in range, marking this commit as GOOD")
                    sys.exit(0)
                else:
                    print("Match is not in range, marking this commit as BAD")
                    sys.exit(1)

    # if we made it this far, something weird went wrong
    print('*** Could not identify line match in EIO, aborting bisection process')
    sys.exit(128)
except subprocess.CalledProcessError:
    print('*** An error occurred trying to run EnergyPlus -- returning 125 to skip this commit')
    sys.exit(125)
