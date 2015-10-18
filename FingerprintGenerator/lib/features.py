import Feature
import numpy as np
from scikits.audiolab import wavread


class Feature_FreqDom(Feature.Feature):

    """
    Implementation of Feature.

    USES: amplitude vs time data.
    """

    def __init__(self, data):
        Feature.Feature.__init__(self, data)

    def initialize(self, data):
        self.freqData = np.fft.fft(data) #into frequency domain



import sys
def main(argv):

    ampData, fs, enc = wavread("/home/damian/Music-Genre-Classification/FingerprintGenerator/TestSongs/Rap/Eminem-Stan.wav")

    feature1 = Feature_FreqDom(ampData[50000:60000])


if __name__ == "__main__":
    main(sys.argv[1:])
