'''
Classes to hold Data segments as found in .azr files.
'''

import numpy as np
import utility

INCLUDE_INDEX = 0
IN_CHANNEL_INDEX = 1
OUT_CHANNEL_INDEX = 2
FILENAME_INDEX = 11

class Segment:
    '''
    Structure to organize the information contained in a line in the
    <segmentsData> section of an AZURE2 input file.
    '''
    def __init__(self, row):
        self.row = row.split()
        self.include = (int(self.row[INCLUDE_INDEX]) == 1)
        self.in_channel = int(self.row[IN_CHANNEL_INDEX])
        self.out_channel = int(self.row[OUT_CHANNEL_INDEX])
        self.filename = self.row[FILENAME_INDEX]
        
        self.values_original = np.loadtxt(self.filename)
        self.values = np.copy(self.values_original)
        self.n = self.values.shape[0]

        if self.out_channel != -1:
            self.output_filename = f'AZUREOut_aa={self.in_channel}_R={self.out_channel}.out'
        else:
            self.output_filename = f'AZUREOut_aa={self.in_channel}_TOTAL_CAPTURE.out'

    
    def string(self):
        '''
        Returns a string of the text in the segment line.
        '''
        row = self.row.copy()
        row[INCLUDE_INDEX] = '1' if self.include else '0'
        row[CHANNEL_INDEX] = str(self.channel)
        row[FILENAME_INDEX] = str(self.filename)
        
        return ' '.join(row)


    def update_dir(self, new_dir):
        '''
        Updates the path directory of the segment.
        If modifications are made to the data, the modified data is written to
        an ephemeral directory so that multiple processes can do so
        simultaneously.
        '''
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

        # All segments listed in the file.
        self.all_segments = []
        for row in self.contents[i:j]:
            if row != '':
                self.all_segments.append(Segment(row))

        # All segments included in the calculation.
        self.segments = []
        for seg in self.all_segments:
            if seg.include:
                self.segments.append(seg)

        # Number of data points for each included segment.
        self.ns = [seg.n for seg in self.segments] 

        # Output files that need to be read.
        self.output_files = []
        for seg in self.segments:
            self.output_files.append(seg.output_filename)
        self.output_files = list(np.unique(self.output_files))


    def update_all_dir(self, new_dir):
        '''
        Updates all the path directories of the segments.
        '''
        for seg in self.all_segments:
            seg.update_dir(new_dir)


    def write_segments(self, contents):
        '''
        Writes the segments to contents.
        "contents" is a representation of the .azr file (list of strings)
        This is typically done in preparation for writing a new .azr file.
        '''
        start = contents.index('<segmentsData>')+1
        stop = contents.index('</segmentsData>')

        for (i, segment) in zip(range(start, stop), self.all_segments):
            contents[i] = segment.string()

        return contents
