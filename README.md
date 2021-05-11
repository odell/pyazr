# pyazr

pyazr is a Python module that serves as an interface to AZURE2.

It _accompanies_ AZURE2. The primary goal is to provide an accessible means of
running AZURE2 with a set of R-matrix parameters and reading the output.

## Requirements

[AZURE2](https://azure.nd.edu) must be installed and available at the command
line via `AZURE2`.

[NumPy](https://numpy.org) and [Matplotlib](https://matplotlib.org/) must be
available in order to run the test script in `test` directory.

## Overview

The classes defined in this module are:

1. AZR
2. Parameter
3. Level
4. Output
5. Segment
6. Data

### AZR

Handles communication with AZURE2 and its output.

### Parameter

Defines a sampled or "free" parameter.

### Level

Defines an R-matrix level (a line in the `<levels>` section of the .azr file).

### Output

Data structure for accessing output data. (I got tired of consulting the
extremely well-documented manual for the output file format.)

### Segment

Data structure to organize the information contained in line of the
`<segmentsData>` section of the .azr file.

### Data

Data structure that holds a list of Segments and provides some convenient
functions for applying actions to all of them.

## Example

In the `test` directory there is a Python script (`test.py`) that predicts the
12C(p,gamma) cross section and compares it to the Vogl data.

Note that the script uses NumPy and Matplotlib.

## Installation

Once the repository has been cloned in `location`, the user can simply modify
the path and `import` the relevant modules.

```
import sys
sys.path.append(location)

import azr
import parameter
import utility
import level
import output
```
