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
import matplotlib.pyplot as plt

import model

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
# 2. Produce a band (or "brush") of curves to show the uncertainty.

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

pool = Pool(processes=4)
os.environ['OMP_NUM_THREADS'] = '1'

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

