import os
import sys

import emcee
import corner
import numpy as np
import matplotlib.pyplot as plt

import model

########################################
# 1. Read in test_mcmc.h5 and test and throw out bad walkers

backend = emcee.backends.HDFBackend('test_mcmc.h5')

backend.get_log_prob().shape

ns, nw, nd = backend.get_chain().shape

# estimated (by eye) burn-in period
nb = 100
# ln(probability) = ln(posterior)
lnp = backend.get_log_prob(discard=nb)
# Get the indices of the walkers whose median ln(prob) is greater than 0.
ii = np.where(np.median(lnp, axis=0) > 0)[0]
# How many walkers pass the criteria? And how many were there to start off with?
print(ii.size, nw)

cut_chain = backend.get_chain(discard=nb)
# Give me the walkers that meet the criteria specified.

chain = cut_chain[:, ii, :].reshape(-1, len(model.labels)) #len(model.labels) is just a way to get the number of parameters

########################################
# 4. Extrapolate to low energy.

def extrapolate(theta):
    '''
    Runs AZURE2 with the single test segment in the input file. 
    '''
    le_capture = model.azr.extrapolate(theta,
            extrap_files=['AZUREOut_aa=2_R=1.extrap'])[0]
    return le_capture[:,3]

# Run the extrapolation for one point in the chain so we can easily read the
# energy.
le_capture = model.azr.extrapolate(chain[0], extrap_files=['AZUREOut_aa=2_R=1.extrap'])[0]
energy = le_capture[:,0]

bucket = np.array([extrapolate(theta) for theta in chain])

#----------------------------------------------
#outputfile = open('bucket_contents.dat','w')
#for stuff in bucket:
#  outputfile.write(str(stuff)+'\n')
#outputfile.close()
#---------------------------------------------

quant_16 = [0 for i in range(len(energy))]
quant_50 = [0 for i in range(len(energy))]
quant_84 = [0 for i in range(len(energy))]
lower_range = [0 for i in range(len(energy))]
upper_range = [0 for i in range(len(energy))]
fig = {}
ax = {}
quantOut = open('quantiles.dat','w')
quantOut.write(f'Energy, Q16, Q50, Q84\n')
for i in range(len(energy)):
#  print (bucket[:,i])
  quant_16[i] = np.quantile(bucket[:,i],0.16)
  quant_50[i] = np.quantile(bucket[:,i],0.5)
  quant_84[i] = np.quantile(bucket[:,i],0.84)

  lower_range[i] = quant_50[i] - 3*(quant_50[i]-quant_16[i])
  upper_range[i] = quant_50[i] + 3*(quant_84[i]-quant_50[i])

#  print(f'Quantiles: {quant_16[i]}, {quant_50[i]}, {quant_84[i]}\n')
  quantOut.write(f'{energy[i]}, {quant_16[i]}, {quant_50[i]}, {quant_84[i]}\n')

  fig, ax = plt.subplots()
  fig.patch.set_facecolor('white')
  ax.hist(bucket[:,i],bins=100,range=(lower_range[i], upper_range[i]))
  plt.title(f'E = {energy[i]}')
  plt.savefig(f'plots/sigma_hist_{energy[i]:.2e}.pdf')
  plt.close()
quantOut.close()

