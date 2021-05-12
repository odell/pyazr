'''
Defines the Bayesian model we will use to analyze the Vogl data.
'''

import sys
import os

import numpy as np
from scipy import stats

# Get the current path so we can import classes defined in the parent directory.
pwd = os.getcwd()
i = pwd.find('/test')
# Import pyazr classes.
sys.path.append(pwd[:i])
from azr import AZR
from parameter import Parameter
########################################
# Set up AZR object and data.

parameters = [
    Parameter(1/2, -1, 'width', 1),
    Parameter(1/2, 1, 'energy', 1),
    Parameter(1/2, 1, 'width', 1),
    Parameter(1/2, 1, 'width', 2)
]

# The number of parameters = number of R-matrix parameters.
nrpar = len(parameters)
nd = nrpar

labels = [
    r'$C_{1/2-}$',
    r'$E_{1/2+}$',
    r'$\Gamma_{1/2+,p}$',
    r'$\Gamma_{1/2+,\gamma}$'
]

# We have to tell AZURE2 which output files it should look at.
# (This could/should be inferred from the data segments in the .azr file.)
# R=2 => particle pair 2
output_files = ['AZUREOut_aa=1_R=2.out']

# We have all of the information we need to instantiate our AZR object.
azr = AZR('12C+p.azr', parameters, output_files)
azr.root_directory = '/tmp/'

# We'll read the data from the output file since it's already in the
# center-of-mass frame.
data = np.loadtxt('output/' + output_files[0])
x = data[:, 0] # energies
y = data[:, 5] # cross sections
dy = data[:, 6] # cross section uncertainties

########################################
# Next, let's set up the Bayesian calculation. Recall:
# * lnP \propto lnL + lnPi
# where
# * P = posterior
# * L = likelihood
# * Pi = prior

# We'll work from right to left.
# First, we need prior disributions for each sampled parameters.
priors = [
    stats.uniform(0, 5),
    stats.uniform(1, 5),
    stats.uniform(0, 50000),
    stats.uniform(-100, 200)
]

def lnPi(theta):
    return np.sum([pi.logpdf(t) for (pi, t) in zip(priors, theta)])


# To calculate the likelihood, we generate the prediction at theta and compare
# it to data. (Assumes data uncertainties are Gaussian and IID.)
def lnL(theta):
    mu = azr.predict(theta)
    capture = mu[0].xs_com_fit
    return np.sum(-np.log(np.sqrt(2*np.pi)*dy) - 0.5*((y - capture)/dy)**2)


def lnP(theta):
    lnpi = lnPi(theta)
    # If any of the parameters fall outside of their prior distributions, go
    # ahead and return lnPi = -infty. Don't bother running AZURE2 or risking
    # calling it with a parameter value that will throw an error.
    if lnpi == -np.inf:
        return lnpi
    return lnL(theta) + lnpi

