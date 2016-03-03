
import sys
from scikits.audiolab import wavread
import matplotlib.pyplot as plt
from collections import deque
import math
import numpy as np

"""
If plt.show() is not working:
http://www.stevenmaude.co.uk/posts/installing-matplotlib-in-virtualenv

"""



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

def FrequencyAtFFTIndex(sampleIndex, fftLength, sampleRateHz=44100):
    """
    Calculates the frequency of the given sample in a FFT result (frequency domain).

    fftLength -> the already split in half length
    """

    return sampleIndex * (sampleRateHz / 2.0) / float(fftLength)

def indexOfFFTFreq(frequency, fftLength, sampleRateHz=44100):
    return (frequency / (sampleRateHz / 2.0)) * float(fftLength)

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


def get_freq_band_index(i, bands, max_i):
    """
    Returns the associeted index of the band for the given frequency.

    Exponential distribution
    """
    n = bands # number of bands

    exp_ratio = 1.4 # the larger this value, the greater the logarithmic difference in bin sizes is going to be


    x = (float(i) / max_i) * exp_ratio
    y = (pow(math.e, x) - 1.0)

    max = (pow(math.e, exp_ratio) - 1.0)
    bin = (y / max) * n
    return int(bin)


# Algorithm from:
# http://www.flipcode.com/misc/BeatDetectionAlgorithms.pdf
# https://www.clear.rice.edu/elec301/Projects01/beat_sync/beatalgo.html#filterbank
def main(args):

    # Load up the song (must be .wav) into memory
    amp_data, fs, enc = wavread(args[0])

    AMP_MAX = 10000
    # list of BPMs to match
    BPMs = range(30, 180, 5)
    # period = (60 / x seconds / beat) * (44100 samples / second) = (60 / x) (44100) samples / beat


    # analyze 5 seconds from the middle of the song
    middle = len(amp_data)/2
    five_seconds = [item[0] + item[1] for item in amp_data[middle:middle + 44100 * 5]]

    # compute the FFT of the 5 second portion
    N = len(five_seconds)
    song_fft = np.fft.fft(five_seconds)[0:N / 2] # cut off repeated FFT data

    numb_bands = 6
    bands = [ [] for i in range(0, numb_bands)]

    # for i in range(len(song_fft)):
    #     bands[get_freq_band_index(i, 8, len(song_fft))].append(song_fft[i])
    hz_0 = 0
    hz_200 = indexOfFFTFreq(200, len(song_fft)) #200 HZ
    hz_400 = indexOfFFTFreq(400, len(song_fft)) #400 HZ
    hz_800 = indexOfFFTFreq(800, len(song_fft)) #800 HZ
    hz_1600 = indexOfFFTFreq(1600, len(song_fft)) #1600 HZ
    hz_3200 = indexOfFFTFreq(3200, len(song_fft)) #3200 HZ
    hz_6400 = indexOfFFTFreq(6400, len(song_fft)) #6400 HZ

    bands[0] = song_fft[hz_0:hz_200]
    bands[1] = song_fft[hz_200:hz_400]
    bands[2] = song_fft[hz_400:hz_800]
    bands[3] = song_fft[hz_800:hz_1600]
    bands[4] = song_fft[hz_1600:hz_3200]
    bands[5] = song_fft[hz_3200:-1]

    bands[0] = bands[0] + list(reversed(bands[0]))
    bands[1] = bands[1] + list(reversed(bands[1]))
    bands[2] = bands[2] + list(reversed(bands[2]))
    bands[3] = bands[3] + list(reversed(bands[3]))
    bands[4] = bands[4] + list(reversed(bands[4]))
    bands[5] = bands[5] + list(reversed(bands[5]))


    fft_bands = [np.fft.ifft(band) for band in bands]


    fig, axs = plt.subplots(nrows=2, ncols=1)
    x = range(0, len(bands[0]))
    y = bands[0]
    axs[0].bar(x, y, facecolor='b', alpha=0.5, linewidth=1, width=1)
    axs[0].set_ylabel('')
    axs[0].set_xlabel('')

    plt.savefig("graphs/" + args[0].split('/')[-1] + "_graph.png")
















    # compute the impulse train for each period






import os
from os.path import isfile, join
if __name__ == "__main__":

    # folder = "/home/damian/Music/Dubstep/"
    #
    # allFiles = [file for file in os.listdir(folder) if file.endswith(".wav")]
    #
    # for file in allFiles:
    #     print file
    #     main([folder + file])
    main(sys.argv[1:])