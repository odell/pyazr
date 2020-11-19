# pyazr

pyazr is a Python module that serves as an interface to AZURE2.

It _accompanies_ AZURE2. The primary goal is to provide an accessible means of
running AZURE2 with a set of R-matrix parameters and reading the output.

## Requirements

[AZURE2](https://azure.nd.edu) must be installed and available at the command
line via `AZURE2`.

## Overview

The classes defined in this module are:

1. AZR
2. Parameter
3. Level
4. Output

### AZR

Handles communication with AZURE2 and its output.

### Parameter

Defines a sampled or "free" parameter.

### Level

Defines an R-matrix level (a line in the `<levels>` section of the .azr file).

### Output

Data structure for accessing output data. (I got tired of consulting the
extremely well-documented manual for the output file format.)

## Example

```
from pyazr import AZR
from parameter import Parameter

parameters = [Parameter(Parameter(1/2, -1, 'width', 1)]

azr = AZR('example.azr', parameters, ['AZUREOut_aa=1_R=1.out'])

channel1 = azr.predict([3.0])

plot(channel1.e_com, channel1.xs_com_fit)
```
