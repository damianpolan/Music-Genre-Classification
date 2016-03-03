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
        newFeature.value = float(serialized)
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
        newFeature.value = int(serialized)
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
        newFeature.value = float(serialized)
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

        if count == 0:
            average = 0
        else:
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
        newFeature.value = float(serialized)
        return newFeature


class Feature_Centroid_SD(Feature.Feature):

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

        centroids = list()
        for samplePack in data:
            centroids.append(tools.Centroid(samplePack))

        self.value = tools.StandardDeviation(centroids)

    def serialize(self):
        """
        Format:
        <length>:::<packed data>
        """

        return float(self.value)

    @staticmethod
    def unserialize(serialized):
        newFeature = Feature_Centroid(None)
        newFeature.value = float(serialized)
        return newFeature


class Feature_Rolloff_SD(Feature.Feature):

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

        falloffs = list()
        for samplePack in data:
            falloffs.append(tools.RollOff(samplePack))

        self.value = tools.StandardDeviation(falloffs)

    def serialize(self):
        """
        Format:
        <length>:::<packed data>
        """

        return float(self.value)

    @staticmethod
    def unserialize(serialized):
        newFeature = Feature_Centroid(None)
        newFeature.value = float(serialized)
        return newFeature


class Feature_Flux(Feature.Feature):

    """
    Implementation of Feature flux function.

    This is a change in amplitude flow over the time domain over the whole song.
    It is calculated by every sample in the song and then averaged rather than per sample back.
    This method avoids loss off data between the last sample of the (i-1)th and the (i)th pack.

    USES: amplitude vs time data.FrequencyAtFFTIndex
    """

    requireFullSong = True

    def __init__(self, data):
        Feature.Feature.__init__(self, data)

    def initialize(self, data):

        prev_magnitude = 0
        total_count = 0
        total_flux = 0

        for sample_pack in data:
            sample_pack = tools.intoMono(sample_pack)
            for i in range(0, len(sample_pack)):
                mag = sample_pack[i]
                total_flux += abs(prev_magnitude - mag)
                total_count += 1
                prev_magnitude = mag

        total_flux /= total_count

        self.value = total_flux

    def serialize(self):
        """
        Format:
        value
        """
        return float(self.value)

    @staticmethod
    def unserialize(serialized):
        newFeature = Feature_Centroid(None)
        newFeature.value = float(serialized)
        return newFeature



class Feature_Spec_Flux_Avg(Feature.Feature):

    """
    Implementation of Feature spectral flux function.
    Spectral flux is calculated over the frequency domain.

    USES: amplitude vs time data.FrequencyAtFFTIndex
    """

    requireFullSong = True

    def __init__(self, data):
        Feature.Feature.__init__(self, data)

    def initialize(self, data):
        sum = 0
        count = 0

        for i in range(1, len(data)):
            sum += tools.Spectral_Flux(data[i-1], data[i])
            count += 1

        average = sum / count

        self.value = average

    def serialize(self):
        """
        Format:
        value
        """
        return float(self.value)

    @staticmethod
    def unserialize(serialized):
        newFeature = Feature_Centroid(None)
        newFeature.value = float(serialized)
        return newFeature



class Feature_Spec_Flux_SD(Feature.Feature):

    """
    Implementation of Feature spectral flux function.
    Spectral flux is calculated over the frequency domain.

    USES: amplitude vs time data.FrequencyAtFFTIndex
    """

    requireFullSong = True

    def __init__(self, data):
        Feature.Feature.__init__(self, data)

    def initialize(self, data):
        fluxes = []
        for i in range(1, len(data)):
            fluxes.append(tools.Spectral_Flux(data[i-1], data[i]))

        self.value = tools.StandardDeviation(fluxes)

    def serialize(self):
        """
        Format:
        value
        """
        return float(self.value)

    @staticmethod
    def unserialize(serialized):
        newFeature = Feature_Centroid(None)
        newFeature.value = float(serialized)
        return newFeature




class Feature_BPM(Feature.Feature):

    #
    """
    http://stackoverflow.com/questions/657073/how-to-detect-the-bpm-of-a-song-in-php
    http://marsyasweb.appspot.com/assets/docs/sourceDoc/html/classMarsyas_1_1BeatReferee.html#details

    Working Demo:
        https://www.youtube.com/watch?v=jZoQ1S73Bac
        http://beetnik.fds.im/
        JSFIDDLE:
        http://jsfiddle.net/eldog/hspz9cp8/

    Algorithm:
    http://archive.gamedev.net/archive/reference/programming/features/beatdetection/index.html
    """

    requireFullSong = True

    def __init__(self, data):
        Feature.Feature.__init__(self, data)

    def initialize(self, data):

        self.value = 120

    def serialize(self):
        """
        Format:
        value
        """
        return int(self.value)

    @staticmethod
    def unserialize(serialized):
        newFeature = Feature_Centroid(None)
        newFeature.value = float(serialized)
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
