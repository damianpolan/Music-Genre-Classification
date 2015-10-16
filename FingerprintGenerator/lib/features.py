import Feature
import numpy as np
import cpickle


class Feature_FreqDom(Feature):

    """
    Implementation of Feature.

    USES: amplitude vs time data.
    """

    def __init__(self):
        pass

    def __init__(self, data):
        self.freqData = intoFrequencyDomain(data)

    def intoFrequencyDomain(data):
        return np.fft.fft(data)

    def serialize(self):
        return cpickle.dumps()

    @staticMethod
    def unserialize(serialized):
        newObj = Feature_FreqDom()
        newObj.freqData = cpickle.loads(serialized)


def main(argv):

    ampData, fs, enc = wavread("/home/damian/Music-Genre-Classification/FingerprintGenerator/TestSongs/Rap/Eminem-Stan.wav")

    feature1 = Feature_FreqDom(ampData[50000:60000])

if __name__ == "__main__":
    main(sys.argv[1:])
