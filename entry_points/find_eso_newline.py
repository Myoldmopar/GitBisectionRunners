#!/usr/bin/env python3

import os
import subprocess
import sys

# build directory needs to have BUILD_FORTRAN configured ON so ReadVars can be executed
BuildDir = '/eplus/repos/4eplus/builds/r'
ProductsDir = '/eplus/repos/4eplus/builds/r/Products'
FileToRun = '/eplus/repos/4eplus/testfiles/1ZoneUncontrolled.idf'


print('*** Changing to build directory ' + BuildDir)
os.chdir(BuildDir)
print('*** Attempting to build EnergyPlus')
try:
    subprocess.check_call(['make', '-j', '4'])
except subprocess.CalledProcessError:
    print('*** An error occurred trying to build EnergyPlus -- returning 125 to skip this commit')
    sys.exit(125)
print('*** Changing to binary dir ' + ProductsDir)
os.chdir(ProductsDir)
print('*** Running EnergyPlus with ReadVars and gathering output')
try:
    output_bytes = subprocess.check_output(['./energyplus', '-r', '-D', FileToRun])
    if b'Blank line in middle of processing' in output_bytes:
        print('*** Detected blank line warning, returning 1 to mark this commit as BAD')
        sys.exit(1)
    else:
        print('*** No blank line warning, returning 0 to mark this commit as GOOD')
        sys.exit(0)
except subprocess.CalledProcessError:
    print('*** An error occurred trying to run EnergyPlus -- returning 125 to skip this commit')
