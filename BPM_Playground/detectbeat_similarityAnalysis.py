
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


def Cross_Correlate_Waves(wav1, wav2):
    pass



# Algorithm from:
# http://www.flipcode.com/misc/BeatDetectionAlgorithms.pdf
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
    song_fft = np.fft.fft(five_seconds)[0:N] # cut off repeated FFT data

    correlation_energies = []
    # create FFT wave for each impulse wave generated from the corresponding BPM
    for bpm in BPMs:
        period = int((60.0 / bpm) * 44100)

        impulse_train = [0] * N
        # generate the impulse_train
        for k in range(0, N):
            if k % period == 0:
                impulse_train[k] = AMP_MAX

        imptrain_fft = np.fft.fft(impulse_train)[0:N] #ti[k] & tj[k]

        # calculate the correlation between the two waves imptrain_fft & song_fft
        correlation_energy = 0
        for k in range(0, len(song_fft)):
            correlation_energy += abs(song_fft[k] * imptrain_fft[k])

        correlation_energies.append(correlation_energy)
        #print str(bpm) + ": \t" + str(correlation_energy)

    largest_i = 0
    for i in reversed(range(0, len(BPMs))):
        if correlation_energies[i] > correlation_energies[largest_i]:
            largest_i = i

    print "BPM: " + str(BPMs[largest_i])


    fig, axs = plt.subplots(nrows=2, ncols=1)
    x = BPMs
    y = correlation_energies
    axs[0].bar(x, y, facecolor='b', alpha=0.5, linewidth=1, width=1)
    axs[0].set_ylabel('E_BPMs')
    axs[0].set_xlabel('BPM')

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