
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




def main(args):

    # Load up the song (must be .wav) into memory
    amp_data, fs, enc = wavread(args[0])

    #############################################
    #   Maintainance of all calculated energies
    #   and average energies:
    #############################################
    energy_spikes = []
    energy_averages = []
    energy_averages_SDs = []
    energies = []


    #############################################
    #   Iteration over sample packs of song:
    #############################################
    # static paramaters
    SAMPLE_PACK_SIZE = 256 / 2
    ENERGY_HISTORY_SIZE = int((44100) / SAMPLE_PACK_SIZE)
    THRESHOLD_C = 1.3

    # contains the last <ENERGY_HISTORY_SIZE> energies
    energy_history = deque(maxlen=ENERGY_HISTORY_SIZE)


    start = int(len(amp_data) * 0.2)
    end = start + (44100 * 20) # 60 sec
    # cuts off the extra samples at the end.
    nthIndex = range(start, end - ((end - start) % SAMPLE_PACK_SIZE), SAMPLE_PACK_SIZE)
    
    for i in nthIndex:
        sample_pack = amp_data[i:i + SAMPLE_PACK_SIZE]

        # calculate the instance energy (squared) of this sample pack
        energy = average(squared(sample_pack), isLR=True)

        # append the instance energy to the right of the history list
        energy_history.append(energy)


        if len(energy_history) >= ENERGY_HISTORY_SIZE:
            # the history buffer is full so we can begin comparing average energy

            energies.append(energy)

            average_energy = average(energy_history)
            #average_energy_SD = standard_dev(energy_history, average_energy)
            average_energy_diff = linear_dev(energy_history, average_energy)

            energy_averages.append(average_energy)
            energy_averages_SDs.append(average_energy_diff)

           # determined_thresh = average_energy * (THRESHOLD_C + 0.5 *
            determined_thresh = average_energy * 1.3 - 0.5 * average_energy_diff


            # print determined_C
            # check for energy spike
            if energy > determined_thresh:
                # we have an energy spike!
                energy_spikes.append(energy)
            else:
                # no spike
                energy_spikes.append(0)



    #############################################
    #   METHOD 1:
    #   FFT on the energy spikes to determin BPM
    #############################################


    # eft = []
    # for e in energy_spikes:
    #     if(e > 0.01):
    #         eft.append(1)
    #     else:
    #         eft.append(0)
    #
    # energy_spikes = eft
    #
    # fftd = np.fft.fft(energy_spikes)
    # # fftd = np.fft.fft(energy_spikes)
    #
    # freq_data = []
    # # convert complex to real
    # for i in range(len(fftd) / 2):
    #     freq_data.append(float((fftd[i].real)))
    #
    # # finds the 50 maximum amplitude frequencies
    # # obj format: (amp, index)
    # max_freq_amps = find_n_maxes(freq_data[1:len(freq_data)], 50)
    #
    # frequency_bpm = -1
    # curr_amp_index = 0
    #
    # lowerBound = 110
    # upperBound = 170
    # while frequency_bpm < lowerBound or frequency_bpm > upperBound:
    #     if (curr_amp_index >= len(max_freq_amps)):
    #         lowerBound -= 10
    #         upperBound += 10
    #         curr_amp_index = 0
    #     frequency_hz = FrequencyAtBinIndex(max_freq_amps[curr_amp_index][1], len(freq_data))
    #     frequency_bpm = frequency_hz * 60
    #     curr_amp_index += 1
    #     print "Determined a BPM of " + str(frequency_bpm) + " for " + str(curr_amp_index) + "th highest frequency."
    #
    #
    #
    # print "BPM: " + str(frequency_bpm)



    #############################################
    #   METHOD 2:
    #   Find the BPM which hits the most spikes and misses the least
    #############################################


    # non_zero_spikes = [e for e in energy_spikes if e >= 0.01 ]

    # pick a period
    #period = 

    # sum the distances of the closest peak
    # if the sum is close to 0, we dont need to shift
    # if the sum is not close to 0, we need to shift
    # unless we have a large SD
    # We want to reduce the SD
    # local maximum search for (Sum of intersecting weights / SD)


    #############################################
    # METHOD 3:
    # Cross correlation
    #############################################



    AMP_MAX = 10000
    # list of BPMs to match
    BPMs = range(60, 170, 1)
    # period = (60 / x seconds / beat) * (44100 samples / second) = (60 / x) (44100) samples / beat


    # analyze 5 seconds from the middle of the song
    middle = len(energy_spikes)/2
    five_seconds = energy_spikes#[middle:middle + (44100 * 5 / SAMPLE_PACK_SIZE)]

    # compute the FFT of the 5 second portion
    N = len(five_seconds)
    song_fft = np.fft.fft(five_seconds)[0:N / 2] # cut off repeated FFT data

    correlation_energies = []
    # create FFT wave for each impulse wave generated from the corresponding BPM
    for bpm in BPMs:
        period = int((60.0 / bpm) * 44100 / SAMPLE_PACK_SIZE)

        impulse_train = [0] * N
        # generate the impulse_train
        for k in range(0, N):
            if k % period == 0:
                impulse_train[k] = AMP_MAX

        imp_train_fft = np.fft.fft(impulse_train)[0:N / 2] # cut off repeated FFT data

        # calculate the correlation between the two waves imptrain_fft & song_fft
        correlation_energy = 0
        for k in range(0, len(song_fft)):
            correlation_energy += abs(song_fft[k] * imp_train_fft[k])

        correlation_energies.append(correlation_energy + -0.01 * bpm)
        # print str(bpm) + ": \t" + str(correlation_energy)


    # we need to apply an equalizer here as generally, the higher the frequency the signal,
    # the more overlap we have
    # for this we create a linear factor based on frequency. The line can be imagined
    # to be going from the first

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

    x = range(0, len(energy_spikes))
    y = energy_spikes
    #axs[1].scatter(x, y, marker="|")
    axs[1].bar(x, y, color='g', linewidth=0)
    axs[1].set_ylabel('Energy')
    axs[1].set_xlabel('Frame')

    plt.savefig("graphs/" + args[0].split('/')[-1] + "_graph.png")
    #############################################
    #   Graphing
    #
    #   Histogram: http://matplotlib.org/users/pyplot_tutorial.html
    #############################################
    # print "Graphing"
    #
    #
    # plt.figure(1)
    # plt.subplot(411)
    #
    #
    #
    # #x = range(0, len(energy_spikes))
    # x = [ i / (44100 / 1024) for i in range(0, len(energy_averages_SDs)) ]
    #
    # #plt.bar(x, energies, facecolor='g', alpha=0.3, linewidth=0, width=1)
    #
    # #plt.bar(x, energy_averages, facecolor='b', alpha=0.4, linewidth=0, width=1)
    #
    # plt.bar(x, energy_spikes, facecolor='g', alpha=1, linewidth=0, width=0.25)
    #
    #
    # plt.title('Beat Analysis')
    # plt.xlabel('Sample Pack')
    # plt.ylabel('Energy')
    # #plt.axis([-500, 4500, 0, 500])
    # plt.grid(True)
    #
    # # Variances
    # plt.subplot(412)
    # x = range(0, len(energy_averages_SDs))
    # plt.bar(x, energy_averages_SDs, facecolor='b', alpha=0.5, linewidth=0, width=5)
    # plt.ylabel('SD')
    # plt.grid(True)
    #
    #
    # # FREQUENCY DOMAIN
    # plt.subplot(413)
    # x = range(1, len(freq_data))
    # plt.bar(x, freq_data[1:len(freq_data)], facecolor='r', alpha=1.0, linewidth=0, width=10)
    # plt.grid(True)
    #
    #
    # # histogram of instance energies
    # plt.subplot(414)
    # plt.hist(non_zero_spikes)
    # plt.grid(True)
    #
    # plt.savefig(args[0] + "_graph.png")

import os

if __name__ == "__main__":

    folder = "/home/damian/Music/Dubstep/"

    allFiles = [file for file in os.listdir(folder) if file.endswith(".wav")]

    for file in allFiles:
        print file
        main([folder + file])
    #main(sys.argv[1:])