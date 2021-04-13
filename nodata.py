'''
Classes to hold Test segments as found in AZURE2 input files.
'''

import numpy as np
import utility

INCLUDE_INDEX = 0
IN_CHANNEL_INDEX = 1
OUT_CHANNEL_INDEX = 2

class TestSegment:
    '''
    Contains a single row within the <segmentsTest> section of a AZURE2 input
    file.
    '''
    def __init__(self, row):
        self.row = row.split()
        self.include = (int(self.row[INCLUDE_INDEX]) == 1)
        self.in_channel = int(self.row[IN_CHANNEL_INDEX])
        self.out_channel = int(self.row[OUT_CHANNEL_INDEX])
        if self.out_channel != -1:
            self.output_filename = f'AZUREOut_aa={self.in_channel}_R={self.out_channel}.extrap'
        else:
            self.output_filename = f'AZUREOut_aa={self.in_channel}_TOTAL_CAPTURE.extrap'


class Test:
    '''
    Structure to hold all of the test segments in a provided AZURE2 input file.
    '''
    def __init__(self, filename):
        self.contents = utility.read_input_file(filename)
        i = self.contents.index('<segmentsTest>')+1
        j = self.contents.index('</segmentsTest>')

        self.all_segments = [] #  all segments in the .azr file
        for row in self.contents[i:j]:
            if row != '':
                self.all_segments.append(TestSegment(row))

        self.segments = [] #  only the segments to be included in the calculation
        for seg in self.all_segments:
            if seg.include:
                self.segments.append(seg)
        
        self.output_files = []
        for seg in self.segments:
            self.output_files.append(seg.output_filename)
        self.output_files = list(np.unique(self.output_files))


    def write_segments(self, contents):
        '''
        Writes the segments to contents.
        "contents" is a representation of the .azr file (list of strings)
        This is typically done in preparation for writing a new .azr file.
        '''
        start = contents.index('<segmentsTest>')+1
        stop = contents.index('</segmentsTest>')

        for (i, segment) in zip(range(start, stop), self.all_segments):
            contents[i] = segment.string()

        return contents

