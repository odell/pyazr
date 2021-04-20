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
from data import Data
from nodata import Test

class AZR:
    '''
    Object that manages the communication between Python and AZURE2.
    input_filename   : .azr file
    parameters       : list of Parameter instances (sampled parameters)
    output_filenames : Which output files (AZUREOut_*.out) are read?
    extrap_filenames : Which output files (AZUREOut_*.extrap) are read?
    '''
    def __init__(self, input_filename, parameters=None, output_filenames=None,
                 extrap_filenames=None):
        self.input_filename = input_filename
        self.input_file_contents = utility.read_input_file(input_filename)
        self.initial_levels = utility.read_levels(input_filename)
        self.data = Data(self.input_filename)
        self.test = Test(self.input_filename)

        '''
        If parameters are not specified, they are inferred from the input file.
        '''
        if parameters is None:
            parameters = []
            jpis = []
            for group in self.initial_levels:
                jpi = group[0].spin*group[0].parity
                jpis.append(jpi)
                for (i, sublevel) in enumerate(group):
                    spin = sublevel.spin
                    parity = sublevel.parity
                    rank = jpis.count(jpi)
                    if i == 0:
                        if not sublevel.energy_fixed:
                            parameters.append(Parameter(spin, parity, 'energy', i+1, rank=rank))
                    if not sublevel.width_fixed:
                        parameters.append(Parameter(spin, parity, 'width', i+1, rank=rank))
        self.parameters = parameters

        '''
        If output files are not specified, they are inferred from the input file.
        '''
        if output_filenames is None:
            self.output_filenames = self.data.output_files
        else:
            self.output_filenames = output_filenames

        '''
        If extrapolation files are not specified, they are inferred from the input file.
        '''
        if extrap_filenames is None:
            self.extrap_filenames = self.test.output_files
        else:
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


    def get_input_values(self):
        '''
        Returns the values of the sampled parameters in the input file.
        '''
        values = [getattr(self.initial_levels[i][j], kind) for (i, j, kind) in
                  self.addresses]
        return values


    def update_data_directories(self, new_dir):
        self.data.update_all_dir(new_dir)
        self.input_file_contents = self.data.write_segments(self.input_file_contents)


    def predict(self, theta, mod_data=False, dress_up=True, full_output=False):
        '''
        Takes:
            * a point in parameter space, theta.
            * dress_up    : Use Output class.
            * full_output : Return reduced width amplitudes as well.
            * mod_data    : Was the data modified since the last evaluation?
        Does:
            * creates a random filename ([rand].azr)
            * creates a (similarly) random output directory (output_[rand]/)
            * writes the new Levels to a [rand].azr
            * writes output directory to [rand].azr
            * runs AZURE2 with [rand].azr
            * reads observable from output_[rand]/output_filename
            * deletes [rand].azr
            * deletes output_[rand]/
        Returns:
            * predicted values a reduced width amplitudes.
        '''
        input_filename, output_dir, data_dir = utility.random_workspace()

        if mod_data:
            self.update_data_directories(data_dir)

        new_levels = self.generate_levels(theta)
        utility.write_input_file(self.input_file_contents, new_levels,
                                 input_filename, output_dir)

        response = utility.run_AZURE2(input_filename, choice=1,
            use_brune=self.use_brune, ext_par_file=self.ext_par_file,
            ext_capture_file=self.ext_capture_file, use_gsl=self.use_gsl)

        if dress_up:
            output = [Output(output_dir + '/' + of) for of in
                      self.output_filenames]
        else:
            output = [np.loadtxt(output_dir + '/' + of) for of in
                      self.output_filenames]

        if full_output:
            output = (output, utility.read_rwas_jpi(output_dir))

        shutil.rmtree(output_dir)
        shutil.rmtree(data_dir)
        os.remove(input_filename)

        return output


    def extrapolate(self, theta, segment_indices=None, use_brune=None,
                    use_gsl=None):
        '''
        See predict() documentation.
        '''
        contents = self.input_file_contents.copy()

        # Map theta to a new list of levels.
        new_levels = self.generate_levels(theta)

        # What extrapolation files need to be read?
        # If the user specifies the indices of the segments, then make sure
        # those are "include"d in the calculation and everything else is
        # excluded.
        t = Test('', contents=contents)
        if segment_indices is not None:
            for (i, test_segment) in enumerate(t.all_segments):
                test_segment.include = i in segment_indices
            t.write_segments(contents)

        # Write the updated contents to the input file and run.
        input_filename, output_dir = utility.random_output_dir_filename()
        utility.write_input_file(contents, new_levels, input_filename,
                                 output_dir)
        response = utility.run_AZURE2(input_filename, choice=3,
            use_brune=use_brune if use_brune is not None else self.use_brune,
            use_gsl=use_gsl if use_gsl is not None else self.use_gsl,
            ext_par_file=self.ext_par_file)

        output = [np.loadtxt(output_dir + '/' + of) for of in
                  t.get_output_files()]

        shutil.rmtree(output_dir)
        os.remove(input_filename)

        return output


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

    
    def ext_capture_integrals(self, use_gsl=False, mod_data=False):
        '''
        Returns the AZURE2 output of external capture integrals.
        '''
        input_filename, output_dir, data_dir = utility.random_workspace()

        if mod_data:
            self.update_data_directories(data_dir)

        new_levels = self.initial_levels.copy()
        new_levels = [l for sl in new_levels for l in sl]
        utility.write_input_file(self.input_file_contents, new_levels,
                                 input_filename, output_dir)
        response = utility.run_AZURE2(input_filename, choice=1,
            use_brune=self.use_brune, ext_par_file=self.ext_par_file,
            ext_capture_file='\n', use_gsl=use_gsl)

        ec = utility.read_ext_capture_file(output_dir + '/intEC.dat')

        shutil.rmtree(output_dir)
        shutil.rmtree(data_dir)
        os.remove(input_filename)

        return ec

    
    def update_ext_capture_integrals(self, segment_indices, shifts, use_gsl=False):
        '''
        Takes:
          * a list of indices to identification which data segment is being
            shifted
          * a list of shifts to be applied (in the same order as the indices are
            provided)
        * Adjusts the energies of data segments (identified by index) by the
        provided shifts (MeV, lab).
        * Evaluates the external capture (EC) integrals.
        * Returns the values from the EC file.
        '''
        for (i, shift) in zip(segment_indices, shifts):
            self.data.segments[i].shift_energies(shift)

        return self.ext_capture_integrals(use_gsl=use_gsl, mod_data=True)
