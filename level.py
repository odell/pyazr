
class Level:
    '''
    Simple data structure for storing the spin (total J), parity (+/-1),
    energy (MeV, excitation), and width (eV) of a level used in an AZURE2
    calculation.

    channel : channel pair (defined in AZURE2)
    radius  : channel radius
    index   : Which spin^{parity} level is this? (There are frequently more than
              one. Consistent with the language, these are zero-based.)
    '''
    def __init__(self, spin, parity, energy, width, radius, channel):
        self.spin = spin
        self.parity = parity
        self.energy = energy
        self.width = width
        self.channel_radius = radius
        self.channel = channel


    def describe(self):
        sign = '+' if self.parity > 0 else '-'
        print(f'{self.spin}{sign} | \
{self.energy} MeV | {self.width} eV | channel {self.channel}')
