import cPickle


class Feature(object):

    """
    Feature is an abstract template class. Should be separately implemented.

    properties
    requireFullSong:    set to true if the entire song is used for computing this property: Rather than a single sample
                        pack, the entire list of packs is passed in as "data" into the initialize function.
    value:  an object or value for the representation of this feature.
    """

    # CONSTRUCTOR
    def __init__(self, data):
        Feature.requireFullSong = False
        if not isinstance(data, type(None)):
            self.initialize(data)

    def initialize(self, data):
        """
        initialize is called when the feature is created. The implemented feature should set its own self.value to the
        result of the feature processing.

        data format: List of left/right amplitude data. i.e a sample pack.
        if the static Feature_X.requireFullSong is True: then a list of data is passed in. I.e a list of sample packs.
        """
        raise "initialize not implemented. Feature is an abstract class."        

    def serialize(self):
        raise "serialize not implemented"

    @staticmethod
    def unserialize(serialized):
        raise "unserialize not implemented"