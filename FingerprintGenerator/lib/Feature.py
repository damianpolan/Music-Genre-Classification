

import cPickle


class Feature(object):

    """
    Feature is an abstract template class. Should be seperately implemented.
    """

    # CONSTRUCTOR
    def __init__(self, data):
        # defines the feature data this feature implementation will use. In the case it is None, raw time domain data will be used. Otherwise, data will be another Feature object.
        self.inputFeature = self.setInputFeature()

        if self.inputFeature == None or data.__class__.__name__ == self.inputFeature:
            self.initialize(data)
        else:
            raise "Incorrect data type. Expected " + str(self.inputFeature)


    def setInputFeature(self):
        raise "Class not implemented. Feature is an abstract class."  

    def initialize(self, data):
        raise "Class not implemented. Feature is an abstract class."        

    def serialize(self):
        return cPickle.dumps(self)

    @staticmethod
    def unserialize(serialized):
        return cPickle.loads(serialized)