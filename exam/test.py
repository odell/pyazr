'''
    Calculates the 12C(p,gamma) cross section and compares it to the Vogl data.
    "Free" parameters:
        * partial width BGP (1/2+, neutron) 
        * level energy (3/2+)
        * partial width (3/2+, neutron)
        * partial width (3/2+, alpha)
'''

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

# Get the current path so we can import classes defined in the parent directory.
pwd = os.getcwd()
i = pwd.find('/test')

# Import pyazr classes.
sys.path.append(pwd[:i])
from azr import AZR
from parameter import Parameter

parameters = [
    Parameter(1/2, 1, 'width', 1, 7),
    Parameter(3/2, 1, 'energy', 1, 3),
    Parameter(3/2, 1, 'width', 1, 3),
    Parameter(3/2, 1, 'width', 2, 3)
]

nd = len(parameters) # number of parameters

labels = [
    r'$C_{1/2+}$',
    r'$E_{3/2+}$',
    r'$\Gamma_{3/2+,n}$',
    r'$\Gamma_{3/2+,\alpha}$'
]

# We have to tell AZURE2 which output files it should look at.
# (This could/should be inferred from the data segments in the .azr file.)
# R=2 => particle pair 2
output_files = ['AZUREOut_aa=2_R=1.out']

azr = AZR('13C+a.azr', parameters, output_files)

# Pick a point (theta) in parameter space at which we can evaluate the capture cross
# section.
theta = [-3.756e7, 7.2393, 313791, 126]

# Calculate the capture cross section at theta (using AZURE2).
output = azr.predict(theta)

# output is a list of Output instances. They are ordered according to the
# output_files list. 
capture = output[0]

# Plot the data.
plt.errorbar(1000*capture.e_com, capture.xs_com_data, yerr=capture.xs_err_com_data,
    linestyle='', label='13C+a')
# Plot the prediction.
plt.plot(1000*capture.e_com, capture.xs_com_fit, label=r'$Prediction$')

plt.yscale('log')
plt.xlabel(r'$E$ (keV, COM)')
plt.ylabel(r'$\sigma$ (b)')
plt.legend()

# Just for kicks let's compute the chi^2/nu.
n = np.size(capture.e_com) # number of data points
chisq = np.sum(((capture.xs_com_data - capture.xs_com_fit) /
    capture.xs_err_com_data)**2)
print(f'chi^2/nu = {chisq/(n-nd)}')

plt.show()
