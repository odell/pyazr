'''
Classes to hold Data segments as found in .azr files.
'''

import numpy as np
import utility

INCLUDE_INDEX = 0
CHANNEL_INDEX = 2
FILENAME_INDEX = 11

class Segment:
    '''
    Structure to organize the information contained in a line in the
    <segmentsData> section of an AZURE2 input file.
    '''
    def __init__(self, row):
        self.row = row.split()
        self.include = (int(self.row[INCLUDE_INDEX]) == 1)
        self.channel = int(self.row[CHANNEL_INDEX])
        self.filename = self.row[FILENAME_INDEX]

        self.values_original = np.loadtxt(self.filename)
        self.values = np.copy(self.values_original)
        self.n = self.values.shape[0]

    
    def string(self):
        row = self.row.copy()
        row[INCLUDE_INDEX] = '1' if self.include else '0'
        row[CHANNEL_INDEX] = str(self.channel)
        row[FILENAME_INDEX] = str(self.filename)
        
        return ' '.join(row)


    def update_dir(self, new_dir):
        i = self.filename.find('/')
        if i >= 0:
            self.filename = new_dir + '/' + self.filename[i+1:]
            np.savetxt(self.filename, self.values)


    def shift_energies(self, shift):
        self.values[:, 0] = self.values_original[:, 0] + shift


class Data:
    '''
    Structure to hold all of the data segments in a provided AZURE2 input file.
    '''
    def __init__(self, filename):
        self.contents = utility.read_input_file(filename)
        i = self.contents.index('<segmentsData>')+1
        j = self.contents.index('</segmentsData>')

        self.all_segments = []
        for row in self.contents[i:j]:
            if row != '':
                self.all_segments.append(Segment(row))

        self.segments = []
        for seg in self.all_segments:
            if seg.include:
                self.segments.append(seg)


    def update_all_dir(self, new_dir):
        for seg in self.all_segments:
            seg.update_dir(new_dir)


    def write_segments(self, contents):
        start = contents.index('<segmentsData>')+1
        stop = contents.index('</segmentsData>')

        for (i, segment) in zip(range(start, stop), self.all_segments):
            contents[i] = segment.string()

        return contents
