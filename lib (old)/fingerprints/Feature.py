import cPickle


class Feature(object):

    """
    Feature is an abstract template class. Should be seperately implemented.
    """

    # CONSTRUCTOR
    def __init__(self, data):
        if not isinstance(data, type(None)):
            self.initialize(data)

    def initialize(self, data):
        raise "initialize not implemented. Feature is an abstract class."        

    def serialize(self):
        raise "serialize not implemented"

    @staticmethod
    def unserialize(serialized):
        raise "unserialize not implemented"