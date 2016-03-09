import abc

from mgc.tools import pcm

from mgc.tools import statistics as stats


####################################################
#   Feature Abstract Class
####################################################

class Feature:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.version = 0

    @abc.abstractmethod
    def calculate(self, pcm_data):
        """
        Calculate the value for this feature.
        :param pcm_data:
        :return:
        """
        return


####################################################
#   Feature Implementations
####################################################

class Centroid_AVG(Feature):
    def __init__(self):
        self.version = 0

    def calculate(self, pcm_data):
        sample_pack_size = 1024

        centroid_avg = stats.average(
                [pcm.centroid(sample_pack)
                 for sample_pack
                 in pcm.to_sample_packs(pcm_data, sample_pack_size)])

        return centroid_avg


class Centroid_SD(Feature):
    def __init__(self):
        self.version = 0

    def calculate(self, pcm_data):
        sample_pack_size = 1024

        centroid_sd = stats.standard_deviation(
                [pcm.centroid(sample_pack)
                 for sample_pack
                 in pcm.to_sample_packs(pcm_data, sample_pack_size)])

        return centroid_sd

