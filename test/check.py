import sys
sys.path.append('/home/odell/pyazr')
from azr import AZR

azr = AZR('12C+p.azr')

for p in azr.parameters:
    p.print()
