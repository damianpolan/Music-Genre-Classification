import struct
import numpy as np
import math


#####################################################
#
#   SERIALIZATION FUNCTIONS
#
#####################################################

def packSongArray(data):
    """
        packs a song array with struct.pack.

        The song array must be an array where each element of the array is another array of two elements. i.e [ [1,2],[3,4],[5,6] ]


        Uses packed format: 
        <length>:::<packed data>
            ** length must be stored for unpacking
    """
    left = []
    right = []
    for pair in data:
        left.append(pair[0])
        right.append(pair[1])

    left.extend(right)
    packed = struct.pack("%sf" % len(left), *left)

    return packed


def unpackSongArray(packed):
    """
    unpacks packed data from packSongArray()
    """
    length = len(packed) / 4 # (4 is length of float)
    unpacked = struct.unpack("%sf" % length, packed)

    data = []

    realLength = int(length) / 2
    for i in range(realLength):
        data.append([unpacked[i], unpacked[i + realLength]])

    return data



#####################################################
#
#   GENERAL HELPER FUNCTIONS
#
#####################################################


def chunks(l, n):
    """
    Splits an array into even size chunks.

    l is the array.
    n is the size of the chunk
    """
    chunked = []
    for i in xrange(0, len(l), n):
        chunked.append(l[i:i+n])
    return chunked




#####################################################
#
#   SAMPLE DATA FUNCTIONS
#
#####################################################

def intoMono(samplePack):
    """
    data = time domain data in list format. Each element in the list should be an array of length two with each subelement being the left/right (stereo) sample.

    output:
        list of sample data in mono format. Each element is the sum of the left/right sample
    """
    return [pair[0] + pair[1] for pair in samplePack]

def intoFrequencyDomain(data):
    #into frequency domain, takes the magnitutde of the complex
    if isinstance(data[0], list): 
        # in stereo format
        if(len(data[0]) != 2):
            raise "Must be list of length 2. For left and right speakers."

        fft = np.fft.fft(data)
        fft = fft[0:len(fft) / 2]
        return [ [abs(pair[0]), abs(pair[1])] for pair in fft]
    else:
        #in mono format

        fft = np.fft.fft(data)
        fft = fft[0:len(fft) / 2] # we remove the last half of the data (the -ve frequencies).
        return [abs(element) for element in fft]

def FrequencyAtFFTIndex(binIndex, fftLength, sampleRateHz=44000):
    """
    Calculates the frequency of the given bin in a FFT result (frequency domain).

    binIndex        The index of the bin to get the frequency for.
    fftLength       The length of the frequency domain list data.
    sampleRateHz:   The sample rate of the audio.

    returns:
        The frequency of the bin. = (binIndex * (sampleRateHz / 2) / fftLength)

    """

    return binIndex * (sampleRateHz / 2) / fftLength


def Centroid(samplePack):
    """
    Calculates the centroid of a given sample pack.
    centroid = sum(f * M(f)) / sum (M(f))
    :param data: time domain data
    :return: centroid value as float
    """
    freq_data = intoFrequencyDomain(intoMono(samplePack))

    sum_fm = 0
    sum_m = 0
    for cbin in range(0, len(freq_data)):
        f = FrequencyAtFFTIndex(cbin, len(freq_data))
        sum_fm += f * freq_data[cbin]  # f * M(f)
        sum_m += freq_data[cbin]  # M(f)

    # handle the divide by zero case!
    if sum_m != 0:
        centroid = sum_fm / sum_m
    else:
        centroid = 0

    return centroid


def RollOff(samplePack):
    freq_data = intoFrequencyDomain(intoMono(samplePack))

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

    return r


def StandardDeviation(values):
    """
    Computes the standard deviation (SD) of a list of values.
    :param values: the values to compute the SD of.
    :return: the SD as a float
    """
    if type(values) is not list:
        raise str("Invalid input exception ")

    n = len(values)
    mean = 0
    for v in values:
        mean += v

    if n == 0:
        return 0

    mean = 0

    sum = 0
    for v in values:
        sum += math.pow(v - mean, 2)

    SD = math.sqrt(sum / n)
    return SD

def Spectral_Flux(pack1, pack2):
    """
    Calculates the average of spectral flux difference between two sample packs.

    The temporal location of pack1 should be before that of pack2.

    :param pack1: (i-1)th sample pack
    :param pack2: (i)th sample pack
    :return:
    """

    fft1 = intoFrequencyDomain(intoMono(pack1))
    fft2 = intoFrequencyDomain(intoMono(pack2))
    fluxes = list()


    for i in range( min(len(fft1), len(fft2))):
        fluxes.append(abs(fft2[i] - fft1[i]))

    sum = 0
    for flux in fluxes:
        sum += flux

    avg = sum / len(fluxes)
    return avg


#####################################################
#
#   LOGGING FUNCTIONS
#
#####################################################

import logging

def defaultLog():
    logging.basicConfig(format='%(asctime)s -   %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)


#####################################################
#
#   FEATURE FUNCTIONS
#
#####################################################
from scikits.audiolab import wavread
import features

def computeFeaturesForFullSong(file_path, feature_list, pack_size):
    """
    Computes each of the features (must be full_song features) for the song recording.
    This method is used for one shot computation of a songs features.
    :param file_path:
    :param features:
    :param pack_size:
    :return: a tuple of values with length = len(features). Each item is the resulting feature value corresponding to features[].
    """

    # will hold the evaluated feature values
    feature_values = []

    raw_data, fs, enc = wavread(file_path)
    raw_chunks = chunks(raw_data, pack_size)

    for feature_name in feature_list:
        # print "Computing " + feature_name
        class_ = getattr(features, feature_name)
        if class_.requireFullSong is False: # ensure full song
            raise "Every feature must be a full song feature"

        feature = class_(raw_chunks)
        feature_values.append(feature.value)

    return feature_values