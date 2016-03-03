
import sys
from scikits.audiolab import wavread
import matplotlib.pyplot as plt
from collections import deque
import math
import numpy as np

import FrequencyAnalysis as fa

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

def get_freq_band_index(i, bands):
    """
    Returns the associeted index of the band for the given frequency.

    Exponential distribution
    """
    n = bands # number of bands
    
    max_sample_i = SAMPLE_PACK_SIZE / 2.0
    exp_ratio = 1.4 # the large this value, the greater the logarithmic difference in bin sizes is going to be

    x = (float(i) / max_sample_i) * exp_ratio
    y = (pow(math.e, x) - 1.0)

    max = (pow(math.e, exp_ratio) - 1.0)
    bin = (y / max) * n
    return int(bin)

# static paramaters
SAMPLE_PACK_SIZE = 1024
ENERGY_HISTORY_SIZE = int(44100 / 1024) # onse second
THRESHOLD_C = 0.5
FREQ_BANDS = 32

def main(args):

    # Load up the song (must be .wav) into memory
    amp_data, fs, enc = wavread(args[0])

    #############################################
    #   Maintainance of all calculated energies
    #   and average energies:
    #############################################

    # list of Spectrum objects
    energies = []
    average_energies = []
    average_energies_SDs = []

    #############################################
    #   Iteration over sample packs of song:
    #############################################

    energy_history = deque(maxlen=ENERGY_HISTORY_SIZE)

    # cuts off the extra samples at the end.
    divider = 10
    amp_data = amp_data[0: int(len(amp_data)/divider)]
    nthIndex = range(0, len(amp_data) - (len(amp_data) % SAMPLE_PACK_SIZE), SAMPLE_PACK_SIZE)


    for i in nthIndex:
        sample_pack = amp_data[i:i + SAMPLE_PACK_SIZE]

        # pull into the frequency domain and split into bands
        sample_pack_fft = np.fft.fft(sample_pack)[0:len(sample_pack) / 2]

        band_energies = [0] * FREQ_BANDS
        band_counts = [0] * FREQ_BANDS

        # Calculates the average energies for each sample pack.
        for i in range(len(sample_pack_fft)):
            band_index = get_freq_band_index(i, FREQ_BANDS)
            band_energies[band_index] += pow(sample_pack_fft[i][0].real, 2) + pow(sample_pack_fft[i][1].real, 2)
            band_counts[band_index] += 1

        for i in range(len(band_energies)):
            if band_counts[i] != 0:
                band_energies[i] /= band_counts[i]

        energy_history.append(band_energies)

        if len(energy_history) >= ENERGY_HISTORY_SIZE:
            energies.append(band_energies)
            average_energies.append([0] * FREQ_BANDS)
            average_energies_SDs.append([0] * FREQ_BANDS)

            for band_number in range(FREQ_BANDS):
                average_energy = average(fa.NthMultiListIterator(energy_history, band_number))
                average_energy_SD = standard_dev(fa.NthMultiListIterator(energy_history, band_number), average_energy)
                average_energies[-1][band_number] = average_energy
                average_energies_SDs[-1][band_number] = average_energy_SD

    #############################################
    #   Graphing
    #
    #   Histogram: http://matplotlib.org/users/pyplot_tutorial.html
    #############################################

   # plt.figure(1)
    fig, axess = plt.subplots(nrows=FREQ_BANDS, ncols=1)
    #fig.tight_layout()
    fig.set_size_inches(8, 2 * FREQ_BANDS)

    for i in range(FREQ_BANDS):
        x = range(0, len(energies))
        y = list(fa.NthMultiListIterator(energies, i))
        axess[i].bar(x, y, facecolor='b', alpha=0.5, linewidth=1, width=1)
        axess[i].set_ylabel('Band ' + str(i))
        axess[i].tick_params(axis='y', labelsize=8)
        axess[i].tick_params(axis='x', labelsize=8)


    plt.savefig("graphs/" + args[0].split('/')[-1] + "_graph.png")





if __name__ == "__main__":
    main(sys.argv[1:])