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
    Yield successive n-sized chunks from l.
    Splits an array into even size chunks.

    l is the array.
    n is the number of chunks

    From: http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]




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
            raise "Must be list of length 2"

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

    mean /= n

    sum = 0
    for v in values:
        sum += math.pow(v - mean, 2)

    SD = math.sqrt(sum / n)
    return SD

#####################################################
#
#   LOGGING FUNCTIONS
#
#####################################################

import logging

def defaultLog():
    logging.basicConfig(format='%(asctime)s -   %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

