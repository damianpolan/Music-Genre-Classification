import math


class NthMultiListIterator:
    """
    Iterates over list, X, returning only the nth (index) object from each list in X.

    I.e iterate over energy_history
    """
    def __init__(self, list, index):
        self.list = list
        self.index = index
        self.curr = 0

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.list[self.index])

    def next(self):
        if self.curr < len(self.list):
            self.curr += 1
            return self.list[self.curr - 1][self.index]
        else:
            raise StopIteration

#
# class Spectrum:
#     """
#     Creates a Logarithmic distribution of a frequency spectrum.
#     """
#     def __init__(self, n_bands, sample_pack_size):
#         self.sample_pack_size = sample_pack_size
#         self.n_bands = n_bands
#         self.bands = [0] * n_bands # each band has an object
#
#     def __len__(self):
#         return len(self.bands)
#
#     def __iter__(self):
#         return self.bands.__iter__()
#
#     def get_band_index_at_freq_index(self, i):
#         """
#         Returns the associated index of the band for the given frequency index. The frequency index is the sample_pack
#         index after an FFT has been applied.
#
#         The bands are exponentially sized so that higher index bands cover a larger portion of frequencies.
#         """
#
#         max_sample_i = self.sample_pack_size / 2.0
#         exp_ratio = 1.4 # the large this value, the greater the logarithmic difference in bin sizes is going to be
#
#         x = (float(i) / max_sample_i) * exp_ratio
#         y = (pow(math.e, x) - 1.0)
#
#         lmax = (pow(math.e, exp_ratio) - 1.0)
#         fbin = (y / lmax) * self.n_bands
#
#         return int(fbin)
#
#     def at_index(self, band_index):
#         """
#         Gets the object associated with a band index
#         :param band_index:
#         :return:
#         """
#         return self.bands[band_index]
#
#     def __getitem__(self, frequency):
#         return self.at_index(self.get_band_index_at_freq_index(frequency))
#
#     def __setitem__(self, frequency):
#         return self.at_index(self.get_band_index_at_freq_index(frequency))
#
