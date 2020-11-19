class Parameter:
    '''
    Defines a sampled (or "free") parameter by spin, parity, channel,
    rank, and whether it's an energy or width (kind).
    kind    : "energy" or "width"
              "width" can be the partial width or ANC (depending on how it was
              set up in AZURE2)
    channel : channel pair (defined in AZURE2; consistent with AZURE2,
              these are one-based)
    rank    : Which spin^{parity} level is this? (There are frequently
              more than one. Consistent with AZURE2, these are 
              one-based.)
    '''
    def __init__(self, spin, parity, kind, channel, rank=1):
        self.spin = spin
        self.parity = parity
        self.kind = kind
        self.channel = int(channel)
        self.rank = rank
