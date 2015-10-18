import cPickle


class Feature(object):

    """
    Feature is an abstract template class. Should be seperately implemented.
    """

    # CONSTRUCTOR
    def __init__(self, data):
        self.initialize(data)


    def setInputFeature(self):
        raise "Class not implemented. Feature is an abstract class."  

    def initialize(self, data):
        raise "Class not implemented. Feature is an abstract class."        

    def serialize(self):
        return cPickle.dumps(self)

    @staticmethod
    def unserialize(serialized):
        return cPickle.loads(serialized)