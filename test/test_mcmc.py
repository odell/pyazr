'''
    Calculates the 12C(p,gamma) cross section and compares it to the Vogl data.
    "Free" parameters:
        * ANC (1/2-)
        * level energy (1/2+)
        * partial width (1/2+, elastic)
        * partial width (1/2+, capture)
'''

import os
import sys
from multiprocessing import Pool

import emcee
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Get the current path so we can import classes defined in the parent directory.
pwd = os.getcwd()
i = pwd.find('/test')

print(pwd[:i])
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

# The number of parameters = number of R-matrix parameters + 1 normalization
# factor.
nrpar = len(parameters)
nd = nrpar + 1

labels = [
    r'$C_{1/2-}$',
    r'$E_{1/2+}$',
    r'$\Gamma_{1/2+,p}$',
    r'$\Gamma_{1/2+,\gamma}$',
    r'$f$'
]

# We have to tell AZURE2 which output files it should look at.
# (This could/should be inferred from the data segments in the .azr file.)
# R=2 => particle pair 2
output_files = ['AZUREOut_aa=1_R=2.out']

# We have all of the information we need to instantiate our AZR object.
azr = AZR('12C+p.azr', parameters, output_files)

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
    stats.uniform(-100, 200),
    stats.uniform(0.5, 1.0)
]

def lnPi(theta):
    return np.sum([pi.logpdf(t) for (pi, t) in zip(priors, theta)])


# To calculate the likelihood, we generate the prediction at theta and compare
# it to data. (Assumes data uncertainties are Gaussian and IID.)
def lnL(theta):
    f = theta[-1] # normalization factor (applied to theory prediction)
    mu = azr.predict(theta[:nrpar]) # AZR object only wants R-matrix parameters
    capture = mu[0].xs_com_fit
    return np.sum(-np.log(np.sqrt(2*np.pi)*dy) - 0.5*((y - f*capture)/dy)**2)


def lnP(theta):
    lnpi = lnPi(theta)
    # If any of the parameters fall outside of their prior distributions, go
    # ahead and return lnPi = -infty. Don't bother running AZURE2 or risking
    # calling it with a parameter value that will throw an error.
    if lnpi == -np.inf:
        return lnpi
    return lnL(theta) + lnpi


########################################
# Finally, we'll set up the sampler and get it started.

nw = 4*nd # number of walkers = 4 * number of sampled parameters

# Pick a point (theta) in parameter space around which we'll start each walker.
theta0 = [2.1, 2.37, 33600, -0.6325, 1.0]
# Each walkers needs its own starting position.
p0 = np.zeros((nw, nd))
for i in range(nw):
    mu = theta0
    sig = np.abs(theta0) * 0.01
    p0[i, :] = stats.norm(mu, sig).rvs()

# We'll store the chain in test_mcmc.h5. (See emcee Backends documentation.)
backend = emcee.backends.HDFBackend('test_mcmc.h5')
backend.reset(nw, nd)

nsteps = 100 # How many steps should each walker take?
nthin = 10 # How often should the walker save a step?
nprocs = 2 # How many Python processes do you want to allocate?
# AZURE2 and emcee are both parallelized. We'll restrict AZURE2 to 1 thread to
# simplify things.
os.environ['OMP_NUM_THREADS'] = '1'

# emcee allows the user to specify the way the ensemble generates proposals.
moves = [(emcee.moves.DESnookerMove(), 0.8), (emcee.moves.DEMove(), 0.2)]

with Pool(processes=nprocs) as pool:
    sampler = emcee.EnsembleSampler(nw, nd, lnP, moves=moves, pool=pool,
            backend=backend)
    state = sampler.run_mcmc(p0, nsteps, thin_by=nthin, progress=True, tune=True)
