import abc
from mgc.tools import pcm
from mgc.tools import stats as stats
from mgc.tools import bpm

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

        pcm_mono = pcm.into_mono(pcm_data)
        pcm_sample_packs = pcm.to_sample_packs(pcm_mono, sample_pack_size)

        centroids = []
        for sample_pack in pcm_sample_packs:
            centroids.append(pcm.centroid(sample_pack))

        centroid_avg = stats.average(centroids)

        return centroid_avg


class Centroid_SD(Feature):
    def __init__(self):
        self.version = 0

    def calculate(self, pcm_data):
        sample_pack_size = 1024

        pcm_mono = pcm.into_mono(pcm_data)
        pcm_sample_packs = pcm.to_sample_packs(pcm_mono, sample_pack_size)

        centroids = []
        for sample_pack in pcm_sample_packs:
            centroids.append(pcm.centroid(sample_pack))

        centroid_sd = stats.standard_deviation(centroids)

        return centroid_sd


class RollOff_AVG(Feature):
    def __init__(self):
        self.version = 0

    def calculate(self, pcm_data):
        sample_pack_size = 1024

        pcm_mono = pcm.into_mono(pcm_data)
        pcm_sample_packs = pcm.to_sample_packs(pcm_mono, sample_pack_size)

        rolloffs = []
        for sample_pack in pcm_sample_packs:
            rolloffs.append(pcm.roll_off(sample_pack))

        rolloff = stats.average(rolloffs)

        return rolloff


class RollOff_SD(Feature):
    def __init__(self):
        self.version = 0

    def calculate(self, pcm_data):
        sample_pack_size = 1024

        pcm_mono = pcm.into_mono(pcm_data)
        pcm_sample_packs = pcm.to_sample_packs(pcm_mono, sample_pack_size)

        rolloffs = []
        for sample_pack in pcm_sample_packs:
            rolloffs.append(pcm.roll_off(sample_pack))

        rolloff_sd = stats.standard_deviation(rolloffs)

        return rolloff_sd


class Flux_AVG(Feature):
    def __init__(self):
        self.version = 1

    def calculate(self, pcm_data):
        sample_pack_size = 1024

        pcm_mono = pcm.into_mono(pcm_data)
        pcm_sample_packs = pcm.to_sample_packs(pcm_mono, sample_pack_size)

        fluxes = []
        for i in range(1, len(pcm_sample_packs)):
            fluxes.append(pcm.spectral_flux(pcm_sample_packs[i - 1], pcm_sample_packs[i]))

        fluxes_sd = stats.average(fluxes)

        return fluxes_sd


class Flux_SD(Feature):
    def __init__(self):
        self.version = 0

    def calculate(self, pcm_data):
        sample_pack_size = 1024

        pcm_mono = pcm.into_mono(pcm_data)
        pcm_sample_packs = pcm.to_sample_packs(pcm_mono, sample_pack_size)

        fluxes = []
        for i in range(1, len(pcm_sample_packs)):
            fluxes.append(pcm.spectral_flux(pcm_sample_packs[i - 1], pcm_sample_packs[i]))

        fluxes_sd = stats.standard_deviation(fluxes)

        return fluxes_sd


class BPM(Feature):
    def __init__(self):
        self.version = 6

    def calculate(self, pcm_data):
        pcm_mono = pcm.into_mono(pcm_data)
        return bpm.determine_bpm(pcm_mono)


class Noise(Feature):
    def __init__(self):
        self.version = 0

    def calculate(self, pcm_data):
        # calculates the time domain zero crossings
        pcm_mono = pcm.into_mono(pcm_data)

        noise = 0

        for i in range(1, len(pcm_mono)):
            sign1 = 1 if pcm_mono[i] > 0 else 0
            sign0 = 1 if pcm_mono[i - 1] > 0 else 0

            noise += abs(sign1 - sign0)

        return noise


class NoiseTwo(Feature):
    def __init__(self):
        self.version = 1

    def calculate(self, pcm_data):
        # calculates the time domain zero crossings
        pcm_mono = pcm.into_mono(pcm_data)

        maximum = 0
        summ = 0

        for sample in pcm_mono:
            summ += abs(sample)
            maximum = max(maximum, abs(sample))

        return (summ / float(maximum)) / len(pcm_mono)





