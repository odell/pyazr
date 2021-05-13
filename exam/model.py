'''
Defines the Bayesian model we will use to analyze the Vogl data.
'''

import sys
import os

import numpy as np
from scipy import stats

# Get the current path so we can import classes defined in the parent directory.
pwd = os.getcwd()
i = pwd.find('/exam')
# Import pyazr classes.
sys.path.append(pwd[:i])
from azr import AZR
from parameter import Parameter
########################################
# Set up AZR object and data.

parameters = [
    Parameter(1/2, -1, 'width', 1, 1),
    Parameter(1/2, 1, 'energy', 1, 1),
    Parameter(1/2, 1, 'width', 1, 1),
    Parameter(1/2, 1, 'width', 2, 1),
    Parameter(3/2, -1, 'energy', 1, 1),
    Parameter(3/2, -1, 'width', 1, 1),
    Parameter(3/2, -1, 'width', 2, 1),
    Parameter(5/2, 1, 'energy', 1, 1),
    Parameter(5/2, 1, 'width', 1, 1)
]

# The number of parameters = number of R-matrix parameters + 3 normalization
# factors.
nrpar = len(parameters)
nd = nrpar + 30

labels = [
    r'$ANC_{1/2-,p}$',
    r'$E_{1/2+}$',
    r'$\Gamma_{1/2+,p}$',
    r'$\Gamma_{1/2+,\gamma}$',
    r'$E_{3/2-}$',
    r'$\Gamma_{3/2-,p}$',
    r'$\Gamma_{3/2-,\gamma}$',
    r'$E_{5/2+}$',
    r'$\Gamma_{5/2+,p}$',
    r'$n_{Ketner}$',
    r'$n_{Ket1}$',
    r'$n_{Ket2}$',
    r'$n_{Ket3}$',
    r'$n_{Ket4}$',
    r'$n_{Ket5}$',
    r'$n_{Ket6}$',
    r'$n_{Ket7}$',
    r'$n_{Ket8}$',
    r'$n_{Ket9}$',
    r'$n_{Ket10}$',
    r'$n_{Ket11}$',
    r'$n_{Ket12}$',
    r'$n_{Ket13}$',
    r'$n_{Burt}$',
    r'$n_{Burt1}$', 
    r'$n_{Burt2}$',
    r'$n_{Burt3}$',
    r'$n_{Burt4}$',
    r'$n_{Burt5}$',
    r'$n_{Burt6}$',
    r'$n_{Burt7}$',
    r'$n_{Vogl}$',
    r'$n_{Rolfs}$',
    r'$n_{Young1}$',   
    r'$n_{Young2}$',
    r'$n_{Young3}$',
    r'$n_{Young4}$',
    r'$n_{Young5}$',
    r'$n_{Meyer}$'
]

# We have to tell AZURE2 which output files it should look at.
# (This could/should be inferred from the data segments in the .azr file.)
# R=2 => particle pair 2
output_files = ['AZUREOut_aa=1_R=1.out', 
                'AZUREOut_aa=1_R=2.out']

ECintfile = ['intEC.dat']

# We have all of the information we need to instantiate our AZR object.
azr = AZR('12C+p.azr', parameters, output_files, ECintfile)

# We'll read the data from the output file since it's already in the
# center-of-mass frame.
scat_data = np.loadtxt('output/' + output_files[0])
capt_data = np.loadtxt('output/' + output_files[1])

x_scat = scat_data[:, 0] # energies
y_scat = scat_data[:, 5] # cross sections
dy_scat = scat_data[:, 6] # cross section uncertainties

x_capt = capt_data[:, 0] # energies
y_capt = capt_data[:, 5] # cross sections
dy_capt = capt_data[:, 6] # cross section uncertainties

x = np.concatenate((x_scat,x_capt))
y = np.concatenate((y_scat,y_capt))
dy = np.concatenate((dy_scat,dy_capt))


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
    stats.uniform(0,5),
    stats.uniform(2.36, 0.02),
    stats.uniform(20000, 40000),
    stats.uniform(-2, 2),
    stats.uniform(3.49, 0.02),
    stats.uniform(40000, 40000),
    stats.uniform(-2, 2),
    stats.uniform(3.53, 0.03),
    stats.uniform(20000, 40000),
    stats.norm(1, 0.08),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.norm(1, 0.1),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.norm(1, 0.1),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.uniform(0.1, 2),
    stats.norm(1, 0.05)
]

def lnPi(theta):
    return np.sum([pi.logpdf(t) for (pi, t) in zip(priors, theta)])


# To calculate the likelihood, we generate the prediction at theta and compare
# it to data. (Assumes data uncertainties are Gaussian and IID.)
def lnL(theta):
    f1 = theta[-30] # normalization factor (applied to theory prediction)
    f2 = theta[-29]
    f3 = theta[-28]
    f4 = theta[-27]
    f5 = theta[-26]
    f6 = theta[-25]
    f7 = theta[-24]
    f8 = theta[-23]
    f9 = theta[-22]
    f10 = theta[-21]
    f11 = theta[-20]
    f12 = theta[-19]
    f13 = theta[-18]
    f14 = theta[-17]
    f15 = theta[-16]
    f16 = theta[-15]
    f17 = theta[-14]
    f18 = theta[-13]
    f19 = theta[-12]
    f20 = theta[-11]
    f21 = theta[-10]
    f22 = theta[-9]
    f23 = theta[-8]
    f24 = theta[-7]
    f25 = theta[-6]
    f26 = theta[-5]
    f27 = theta[-4]
    f28 = theta[-3]
    f29 = theta[-2]
    f30 = theta[-1]

    mu = azr.predict(theta[:nrpar]) # AZR object only wants R-matrix parameters
    
    output_scat = mu[0]
    output_capt = mu[1]
   
    cross_sections_scat = output_scat.xs_com_fit
    cross_sections_capt = output_capt.xs_com_fit    

    cross_sections_1 = cross_sections_scat
    cross_sections_2 = cross_sections_capt[:118]
    cross_sections_3 = cross_sections_capt[118:125]
    cross_sections_4 = cross_sections_capt[125:129]
    cross_sections_5 = cross_sections_capt[129:140]
    cross_sections_6 = cross_sections_capt[140:144]
    cross_sections_7 = cross_sections_capt[144:155]
    cross_sections_8 = cross_sections_capt[155:159]
    cross_sections_9 = cross_sections_capt[159:171]
    cross_sections_10 = cross_sections_capt[171:175]
    cross_sections_11 = cross_sections_capt[175:179]
    cross_sections_12 = cross_sections_capt[179:182]
    cross_sections_13 = cross_sections_capt[182:186]
    cross_sections_14 = cross_sections_capt[186:190]
    cross_sections_15 = cross_sections_capt[190:194]
    cross_sections_16 = cross_sections_capt[194:201]
    cross_sections_17 = cross_sections_capt[201:205]
    cross_sections_18 = cross_sections_capt[205:209]
    cross_sections_19 = cross_sections_capt[209:212]
    cross_sections_20 = cross_sections_capt[212:215]
    cross_sections_21 = cross_sections_capt[215:218]
    cross_sections_22 = cross_sections_capt[218:222]
    cross_sections_23 = cross_sections_capt[222:226]
    cross_sections_24 = cross_sections_capt[226:306]
    cross_sections_25 = cross_sections_capt[306:468]
    cross_sections_26 = cross_sections_capt[468:474]
    cross_sections_27 = cross_sections_capt[474:480]
    cross_sections_28 = cross_sections_capt[480:488]
    cross_sections_29 = cross_sections_capt[488:494]
    cross_sections_30 = cross_sections_capt[494:]

    
#    cross_sections_3 = cross_sections[52:]
#    cross_sections_4 = cross_sections[99:]

#    print(f'{cross_sections_1}, {cross_sections_2}\n')

    normalized_prediction = np.hstack((f1*cross_sections_1, 
                                       f2*cross_sections_2,
                                       f3*cross_sections_3,
                                       f4*cross_sections_4,
                                       f5*cross_sections_5,
                                       f6*cross_sections_6,
                                       f7*cross_sections_7,
                                       f8*cross_sections_8,
                                       f9*cross_sections_9,
                                       f10*cross_sections_10,
                                       f11*cross_sections_11,
                                       f12*cross_sections_12,
                                       f13*cross_sections_13,
                                       f14*cross_sections_14,
                                       f15*cross_sections_15,
                                       f16*cross_sections_16,
                                       f17*cross_sections_17,
                                       f18*cross_sections_18,
                                       f19*cross_sections_19,
                                       f20*cross_sections_20,
                                       f21*cross_sections_21,
                                       f22*cross_sections_22,
                                       f23*cross_sections_23,
                                       f24*cross_sections_24,
                                       f25*cross_sections_25,
                                       f26*cross_sections_26,
                                       f27*cross_sections_27,
                                       f28*cross_sections_28,
                                       f29*cross_sections_29,
                                       f30*cross_sections_30))

    return np.sum(-np.log(np.sqrt(2*np.pi)*dy) - 0.5*((y - normalized_prediction)/dy)**2)


def lnP(theta):
    lnpi = lnPi(theta)
    # If any of the parameters fall outside of their prior distributions, go
    # ahead and return lnPi = -infty. Don't bother running AZURE2 or risking
    # calling it with a parameter value that will throw an error.
    if lnpi == -np.inf:
        return lnpi
    return lnL(theta) + lnpi

