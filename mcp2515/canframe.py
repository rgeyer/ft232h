class CanFrame(object):

    # STD is 11 bits, or 0x7FF
    # EXT is 18 bits, or 0x3FFFF

    def __init__(self, std_id, data, ext_id=None, rtr=False):
