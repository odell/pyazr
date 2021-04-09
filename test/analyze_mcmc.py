'''
Analyzes output of test_mcmc.py.
1. Read in test_mcmc.h5.
2. Produce a corner plot.
3. Produce a band (or "brush") of curves to show the uncertainty in the capture
cross section.
4. Extrapolate to low energy.

The default parameters of test_mcmc.py will not produce a converged run, so
these plots will not look very good. The user will undoubtedly need to run
longer.
'''

import os
import sys
from multiprocessing import Pool

import emcee
import corner
import numpy as np
import matplotlib.pyplot as plt

import model

pool = Pool(processes=1)
os.environ['OMP_NUM_THREADS'] = '1'

########################################
# 1. Read in test_mcmc.h5.

backend = emcee.backends.HDFBackend('test_mcmc.h5')
chain = backend.get_chain(flat=True)

########################################
# 2. Produce a corner plot.

fig = corner.corner(chain, labels=model.labels, quantiles=[0.16, 0.5, 0.84],
        show_titles=True)
fig.patch.set_facecolor('white')
plt.savefig('corner.pdf')

########################################
# 3. Produce a band (or "brush") of curves to show the uncertainty.

def mu(theta):
    '''
    Compute the AZURE2 prediction at theta and applies the normalization factor.
    '''
    f = theta[-1] # normalization factor (applied to theory prediction)
    mu = model.azr.predict(theta[:model.nrpar]) # AZR object only wants R-matrix parameters
    capture = mu[0].xs_com_fit
    return f*capture

# Run an evaluation just to read the energies.
output = model.azr.predict(chain[0])[0]
energies = output.e_com
vogl = output.xs_com_data
vogl_err = output.xs_err_com_data

# The default parameters of test_mcmc.py produce a short chain. When analyzing a
# longer run, one may want to do the evaluation on a subset of the chain.
brush = pool.map(mu, chain)

fig, ax = plt.subplots()
fig.patch.set_facecolor('white')

for stroke in brush:
    ax.plot(energies, stroke, color='C0', alpha=0.1)

ax.errorbar(energies, vogl, yerr=vogl_err, linestyle='', capsize=2, color='C1')
ax.set_xlabel(r'$E$ (MeV, COM)')
ax.set_ylabel(r'$\sigma$ (b)')
ax.set_yscale('log')
plt.savefig('brush.pdf')

########################################
# 4. Extrapolate to low energy.

def extrapolate(theta):
    '''
    Runs AZURE2 with the single test segment in the input file. 
    Returns the cross section at 0.1 MeV (lab).
    '''
    le_capture = model.azr.extrapolate(theta,
            extrap_files=['AZUREOut_aa=1_R=1.extrap'])[0]
    return le_capture[3]

# Run the extrapolation for one point in the chain so we can easily read the
# energy.
le_capture = model.azr.extrapolate(chain[0], extrap_files=['AZUREOut_aa=1_R=1.extrap'])[0]
energy = le_capture[0]

bucket = np.array([extrapolate(theta) for theta in chain])

fig, ax = plt.subplots()
fig.patch.set_facecolor('white')
ax.hist(bucket)
plt.savefig(f'sigma_{energy:.2f}_hist.pdf')
