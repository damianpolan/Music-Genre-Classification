import Feature
import numpy as np
import tools
import logging as log




"""
 SAMPLE PACK FEATURES:
"""
class Feature_FreqDom(Feature.Feature):

    """
    Implementation of Feature.

    USES: amplitude vs time data.
    """
    requireFullSong = False

    def __init__(self, data):
        self.value = None

    def initialize(self, data):
        self.value = tools.intoFrequencyDomain(tools.intoMono(data))

    def serialize(self):
        """
        Format:
        <length>:::<packed data>
        """

        return tools.packSongArray(self.freqData)

    @staticmethod
    def unserialize(serialized):
        new_feature = Feature_FreqDom(None)
        new_feature.value = tools.unpackSongArray(serialized)
        return new_feature


class Feature_Centroid(Feature.Feature):

    """
    Implementation of Feature Centroid function.

    centroid = sum(f * M(f)) / sum (M(f))

    USES: amplitude vs time data.
    """
    requireFullSong = False

    def __init__(self, data):
        Feature.Feature.__init__(self, data)

    def initialize(self, data):
        self.value = tools.centroid(data);

    def serialize(self):
        """
        Format:
        <length>:::<packed data>
        """

        return float(self.value)

    @staticmethod
    def unserialize(serialized):
        newFeature = Feature_Centroid(None)
        newFeature.value = serialized
        return newFeature


class Feature_Rolloff(Feature.Feature):

    """
    Implementation of Feature Rolloff function.

    USES: amplitude vs time data.
    """

    requireFullSong = False

    def __init__(self, data):
        Feature.Feature.__init__(self, data)

    def initialize(self, data):
        self.value = tools.RollOff(data)

    def serialize(self):
        """
        Format:
        value
        """
        return int(self.value)

    @staticmethod
    def unserialize(serialized):
        newFeature = Feature_Centroid(None)
        newFeature.value = serialized
        return newFeature


"""
 FULL SONG FEATURES:
"""

class Feature_Centroid_Avg(Feature.Feature):

    """
    Implementation of Feature Centroid function over a full song. Calculates the average over all sample packs.

    centroid = sum(f * M(f)) / sum (M(f))
     ^ for one sample pack

    USES: amplitude vs time data.
    """
    requireFullSong = True

    def __init__(self, data):
        Feature.Feature.__init__(self, data)

    def initialize(self, data):

        sum = 0
        count = 0

        for samplePack in data:
            sum += tools.Centroid(samplePack)
            count += 1

        average = sum / count

        self.value = average

    def serialize(self):
        """
        Format:
        <length>:::<packed data>
        """

        return float(self.value)

    @staticmethod
    def unserialize(serialized):
        newFeature = Feature_Centroid(None)
        newFeature.value = serialized
        return newFeature


class Feature_Rolloff_Avg(Feature.Feature):
    """
    Implementation of Feature Rolloff function over a full song. Calculates the average over all sample packs.

    USES: amplitude vs time data.
    """
    requireFullSong = True

    def __init__(self, data):
        Feature.Feature.__init__(self, data)

    def initialize(self, data):

        sum = 0
        count = 0

        for samplePack in data:
            sum += tools.RollOff(samplePack)
            count += 1

        average = sum / count

        self.value = average

    def serialize(self):
        """
        Format:
        <length>:::<packed data>
        """

        return float(self.value)

    @staticmethod
    def unserialize(serialized):
        newFeature = Feature_Centroid(None)
        newFeature.value = serialized
        return newFeature

class Feature_Flux(Feature.Feature):

    """
    Implementation of Feature flux function.

    USES: amplitude vs time data.FrequencyAtFFTIndex
    """

    requireFullSong = True

    def __init__(self, data):
        Feature.Feature.__init__(self, data)

    def initialize(self, data):
        freq_data = tools.intoFrequencyDomain(tools.intoMono(data))

        sum_m_total = 0
        for cbin in range(0, len(freq_data)):
            sum_m_total += freq_data[cbin]  # M(f)

        sum_m_target = 0.85 * sum_m_total
        sum_m_new = 0
        r = 0
        for cbin in range(0, len(freq_data)):
            sum_m_new += freq_data[cbin]  # M(f)
            r += 1
            if sum_m_new > sum_m_target:
                break

        self.value = r

    def serialize(self):
        """
        Format:
        value
        """
        return int(self.value)

    @staticmethod
    def unserialize(serialized):
        newFeature = Feature_Centroid(None)
        newFeature.value = serialized
        return newFeature



import sys


def main(argv):

    # ampData, fs, enc = wavread("/home/damian/Music-Genre-Classification/FingerprintGenerator/TestSongs/Rap/Eminem-Stan.wav")

    # feature1 = Feature_FreqDom(ampData[800000:800010])

    # print feature1.freqData
    # print ""
    # print feature1.unserialize(feature1.serialize()).freqData

    actualData = [[0.0426635742188, 0.0431213378906], [0.0339965820312, 0.034423828125], [0.0144653320312, 0.014892578125], [-0.00677490234375, -0.00634765625], [-0.0119018554688, -0.011474609375], [0.00283813476562, 0.0032958984375], [0.0173645019531, 0.0177917480469], [0.0170288085938, 0.0174560546875], [0.0120849609375, 0.0125122070312], [0.00521850585938, 0.00567626953125]]

    TEH_Feature = Feature_FreqDom(actualData)
    print TEH_Feature.freqData


if __name__ == "__main__":
    main(sys.argv[1:])
