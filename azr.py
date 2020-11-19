'''
Defines classes for interacting with AZURE2.
'''

import os
import shutil
import numpy as np
import level
import utility
from parameter import Parameter
from output import Output

class AZR:
    '''
    Object that manages the communication between Python and AZURE2.
    input_filename   : .azr file
    parameters       : list of Parameter instances (sampled parameters)
    output_filenames : Which output files (AZUREOut_*.out) are read?
    extrap_filenames : Which output files (AZUREOut_*.extrap) are read?
    '''
    def __init__(self, input_filename, parameters, output_filenames,
                 extrap_filenames=None):
        self.input_filename = input_filename
        self.input_file_contents = utility.read_input_file(input_filename)
        self.initial_levels = utility.read_levels(input_filename)
        self.parameters = parameters
        self.output_filenames = output_filenames
        self.extrap_filenames = extrap_filenames

        # default values
        self.use_brune = True
        self.use_gsl = True
        self.ext_par_file = '\n'
        self.ext_capture_file = '\n'

        Jpi = [l[0].spin*l[0].parity for l in self.initial_levels] 
        self.addresses = []
        for p in self.parameters:
            jpi = p.spin*p.parity
            i = Jpi.index(jpi)
            i += p.rank-1 # convert from one-based count to zero-based index
            j = p.channel-1 # convert from one-based count to zero-based index
            self.addresses.append([i, j, p.kind])


    def generate_levels(self, theta):
        levels = self.initial_levels.copy()
        for (theta_i, address) in zip(theta, self.addresses):
            i, j, kind = address
            if kind == 'energy':
                '''
                Set the energy for each channel in this level to the prescribed
                energy.
                '''
                for sl in levels[i]:
                    sl.energy = theta_i
            else:
                setattr(levels[i][j], kind, theta_i)
        return [l for sublevel in levels for l in sublevel]


    def predict(self, theta, dress_up=True, full_output=False):
        '''
        Takes a point in parameter space, theta.
        dress_up    : Use Output class.
        full_output : Return reduced width amplitudes as well.
        Does:
            * creates a random filename ([rand].azr)
            * creates a (similarly) random output directory (output_[rand]/)
            * writes the new Levels to a [rand].azr
            * writes output directory to [rand].azr
            * runs AZURE2 with [rand].azr
            * reads observable from output_[rand]/output_filename
            * deletes [rand].azr
            * deletes output_[rand]/
        Returns predicted values a reduced width amplitudes.
        '''
        input_filename, output_dir = utility.random_output_dir_filename()
        new_levels = self.generate_levels(theta)
        utility.write_input_file(self.input_file_contents, new_levels,
                                 input_filename, output_dir)
        response = utility.run_AZURE2(input_filename, choice=1,
            use_brune=self.use_brune, ext_par_file=self.ext_par_file,
            ext_capture_file=self.ext_capture_file, use_gsl=self.use_gsl)

        if dress_up:
            data = [Output(output_dir + '/' + of) for of in
                    self.output_filenames]
        else:
            data = [np.loadtxt(output_dir + '/' + of) for of in
                    self.output_filenames]

        if full_output:
            data = (data, utility.read_rwas_jpi(output_dir))

        shutil.rmtree(output_dir)
        os.remove(input_filename)

        return data


    def extrapolate(self, theta, dress_up=True):
        '''
        See predict() documentation.
        '''
        assert self.extrap_filenames is not None, \
            'No .extrap files specified.'

        input_filename, output_dir = utility.random_output_dir_filename()
        new_levels = self.generate_levels(theta)
        utility.write_input_file(self.input_file_contents, new_levels,
                                 input_filename, output_dir)
        response = utility.run_AZURE2(input_filename, choice=3,
            use_brune=self.use_brune, ext_par_file=self.ext_par_file,
            ext_capture_file=self.ext_capture_file, use_gsl=self.use_gsl)

        if dress_up:
            data = [Output(output_dir + '/' + of) for of in
                    self.output_filenames]
        else:
            data = [np.loadtxt(output_dir + '/' + of) for of in
                    self.output_filenames]

        shutil.rmtree(output_dir)
        os.remove(input_filename)

        return data


    def rwas(self, theta):
        '''
        Returns the reduced width amplitudes (rwas) and their corresponding J^pi
        at the point in parameter space, theta.
        '''
        input_filename, output_dir = utility.random_output_dir_filename()
        new_levels = self.generate_levels(theta)
        utility.write_input_file(self.input_file_contents, new_levels,
                                 input_filename, output_dir)
        response = utility.run_AZURE2(input_filename, choice=1,
            use_brune=self.use_brune, ext_par_file=self.ext_par_file,
            ext_capture_file=self.ext_capture_file, use_gsl=self.use_gsl)

        rwas = utility.read_rwas_jpi(output_dir)

        shutil.rmtree(output_dir)
        os.remove(input_filename)

        return rwas