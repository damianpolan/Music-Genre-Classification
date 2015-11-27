import Feature
import numpy as np
from scikits.audiolab import wavread
import struct
import tools

class Feature_FreqDom(Feature.Feature):

    """
    Implementation of Feature.

    USES: amplitude vs time data.
    """

    def __init__(self, data, useInitialize=True):
        Feature.Feature.__init__(self, data, useInitialize)

    def initialize(self, data):
        self.freqData = tools.intoFrequencyDomain(tools.intoMono(data))
         
    def serialize(self):
        """
        Format:
        <length>:::<packed data>
        """

        return tools.packSongArray(self.freqData)

    @staticmethod
    def unserialize(serialized):
        newFeature = Feature_FreqDom(None, False)
        newFeature.freqData = tools.unpackSongArray(serialized)
        return newFeature


import sys
def main(argv):

    ampData, fs, enc = wavread("/home/damian/Music-Genre-Classification/FingerprintGenerator/TestSongs/Rap/Eminem-Stan.wav")

    feature1 = Feature_FreqDom(ampData[800000:800010])



    print feature1.freqData
    print ""
    print feature1.unserialize(feature1.serialize()).freqData




if __name__ == "__main__":
    main(sys.argv[1:])
