
import sys
from scikits.audiolab import wavread
import matplotlib.pyplot as plt
from collections import deque
import math
import numpy as np

def average(ilist, isLR=False):
    """
    Calculates average value of the list.

    isLR -> whether the list has left/right sound data. ie. list is in format [ [l0,r0], ... [ln,rn]]
    """

    summ = 0
    for sample in ilist:
        if isLR:
            summ += sample[0] + sample[1]
        else:
            summ += sample

    return float(summ) / len(ilist)

def squared(ilist, isLR=False):
    """
    Squares each element in the list. Returns a new list.

    isLR -> whether the list has left/right sound data. ie. list is in format [ [l0,r0], ... [ln,rn]]
    """
    new_list = []
    for sample in ilist:
        if isLR:
            new_list.append(pow(sample[0], 2) + pow(sample[1], 2))
        else:
            new_list.append(pow(sample, 2))

    return new_list


def standard_dev(ilist, avg):
    if not avg: #calculate average if its not already calculated
        avg = average(ilist)

    summ = 0
    for item in ilist:
        summ += pow(item - avg, 2)

    return math.sqrt(float(summ) / (len(ilist) - 1))


def linear_dev(ilist, avg):
    # calculates that average difference of the values in ilist from avg.
    if not avg: #calculate average if its not already calculated
        avg = average(ilist)

    summ = 0
    for item in ilist:
        summ += abs(item - avg)

    return math.sqrt(float(summ) / (len(ilist) - 1))

def FrequencyAtBinIndex(binIndex, fftLength, sampleRateHz=(44100 / 1024)):
    """
    Calculates the frequency of the given bin in a FFT result (frequency domain).

    binIndex        The index of the bin to get the frequency for.
    fftLength       The length of the frequency domain list data.
    sampleRateHz:   The sample rate of the audio.

    returns:
        The frequency of the bin. = (binIndex * (sampleRateHz / 2) / fftLength)

    """

    return binIndex * (sampleRateHz / 2.0) / float(fftLength)



def find_n_maxes(l, n):
    """
    Determines the largest values in a given list. n is the maximum count of maxes to find.

    returns a list of tuples. The first index of the tuple is the maximum value and the second is the index.

    i.e find_n_maxes([2,-4,8], 2) will return:
        [(8,2), (2,0)]


    """
    maxes = []

    shifting = False

    for listI in range(len(l)):
        added = False
        i = 0
        while i < len(maxes):
            if l[listI] > maxes[i][0]:
                maxes = maxes[0:i] + [(l[listI], listI)] + maxes[i:len(maxes)]
                if len(maxes) > n: del maxes[-1]
                added = True
                break
            i += 1

        if not added and len(maxes) < n:
            maxes.append((l[listI], listI))


    return maxes


def normalize(data):
    """
    Normalizes the data to values between 0 and 1
    :param data:
    :return:
    """
    max = data[0]

    for d in data:
        if d > max:
            max = d

    new_list = []
    for d in data:
        new_list.append(max / d)

    return new_list


def avg_around_index(i, c, list):
    """
    Square averages the values around i +/- c

    :param i:
    :param list:
    :return: (average, x) where x is the index which had the highest value
    """

    start_i = i - c
    end_i = i + c # inclusive

    if start_i < 0:
        start_i = 0
    if end_i >= len(list):
        end_i = len(list) - 1

    max_i = start_i
    sum = 0
    for x in range(start_i, end_i + 1):
        sum += list[x] ** 2
        if list[x] >= list[max_i]:
            max_i = x

    return sum / (end_i - start_i + 1), max_i




