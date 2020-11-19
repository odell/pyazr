import numpy as np

class Output:
    '''
    Packages AZURE2 output.
    (See the section of the AZURE2 Manual on output file format.)

    e_com = center-of-mass energy
    e_x = excitation energy
    xs = cross section
    sf = S-factor
    com = center-of-mass
    err = error/uncertainty
    fit = AZURE2 calculation
    data = original data
    '''
    def __init__(self, filename):
        self.contents = np.loadtxt(filename)
        self.e_com = self.contents[:, 0]
        self.e_x = self.contents[:, 1]
        self.angle_com = self.contents[:, 2]
        self.xs_com_fit = self.contents[:, 3]
        self.sf_com_fit = self.contents[:, 4]
        self.xs_com_data = self.contents[:, 5]
        self.xs_err_com_data = self.contents[:, 6]
        self.sf_com_data = self.contents[:, 7]
        self.sf_err_com_data = self.contents[:, 8]
