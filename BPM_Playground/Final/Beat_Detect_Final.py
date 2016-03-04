import os
import sys
import tools
import math
import numpy as np
from scikits.audiolab import wavread
import matplotlib.pyplot as plt
from collections import deque

#http://www.mathworks.com/help/signal/examples/measuring-signal-similarities.html

def correlation_energy(wav1, wav2):
    """
    Determines the similarity between two waves using sum of products.
    """
    correlation_energy = 0
    for k in range(0, len(wav1)):
        correlation_energy += abs(wav1[k] * wav2[k])

    return correlation_energy

#http://en.wikipedia.org/wiki/Mean_squared_error
def mean_squared_error(wav1, wav2):
    """
    Determines the similarity between two waves using mean squared error.
    """
    sum = 0
    for k in range(len(wav1)):
        sum += (wav1[k] - wav2[k]) ** 2

    mean_squared_e = sum / len(wav1)
    return  mean_squared_e

def generate_impulse_train(period, size, amplitude=1):
    """
    Generates an impulse train.
    :param period: the period to generate
    :param size: The size of the output sample list
    :param amplitude: The amplitude of the impulses
    :return: list of amplitudes
    """
    impulse_train = [0] * size
    # generate the impulse_train
    for k in range(0, size):
        if k % period == 0:
            impulse_train[k] = amplitude
    return  impulse_train


def compute_beat_with_impulse_trains(wave, periods):
    """
    Uses an impulse train comparison to determine the beat period of a signal.
    :param periods: the beat periods to check
    :return: the index of periods which is the closes match
    """
    N = len(wave)
    wav_fft = np.fft.fft(wave)[0:N / 2] # remove repeated FFT information

    correlations = []
    for period in periods:
        impulse_train = generate_impulse_train(period, N)
        impulse_train_fft = np.fft.fft(impulse_train)
        correlation = correlation_energy(wav_fft, impulse_train_fft) * mean_squared_error(wav_fft, impulse_train_fft)
        correlations.append(correlation)

    # we need to equalize the correlations as they will tend to trend linearly upward as the period decreases
    slope, offsety = compute_best_fit_line(correlations)

    for i in range(len(correlations)):
        correlations[i] += -slope * i

    # computes the area where the larges considered i will be in
    # takes the i which has the highest value in that area
    c = 4 # area around i to average
    largest_i_area = 0
    largest_i = 0
    for i in range(0, len(correlations)):
        # wierd max here.
        v_curr, x = tools.avg_around_index(i, c, correlations)
        v_larg, x1n = tools.avg_around_index(largest_i_area, c, correlations)

        if  v_curr >= v_larg:
            largest_i_area = i
            largest_i = x

    # return largest_i_area... wierd i know but gives better results
    return  largest_i_area, correlations


def compute_best_fit_line(data):
    """
    Computs the line of best fit for a list of values. Assumes x value is the index of the item in the list.
    http://hotmath.com/hotmath_help/topics/line-of-best-fit.html
    :param data: list of data points
    :return: (m, b) or .. (slope, yoffset)
    """
    avg_x = len(data) / 2
    avg_y = tools.average(data)
    xXyY = 0
    xX2 = 0

    for x in range(len(data)):
        xXyY += (x - avg_x) * (data[x] - avg_y)
        xX2 += math.pow(x - avg_x, 2)

    slope_m = xXyY / xX2
    yoffet_b = avg_y - slope_m * avg_x
    return  slope_m, yoffet_b


def pearsons_product_moment(wavx, wavy):
    """
    https://en.wikipedia.org/wiki/Correlation_and_dependence
    :param wav1:
    :param wav2:
    :return:
    """
    avg_x = tools.average(wavx)
    avg_y = tools.average(wavy)

    xXyY = 0
    xX2 = 0
    yY2 = 0

    for i in range(len(wavx)):
        xXyY += (wavx[i] - avg_x) * (wavy[i] - avg_y)
        xX2 += math.pow(wavx[i] - avg_x, 2)
        yY2 += math.pow(wavy[i] - avg_y, 2)

    r = xXyY / (math.sqrt(xX2 * yY2))
    return r


#def break_into_bands(wav, numb_bands):



def main(args):

    # Load up the song (must be .wav) into memory
    amp_data, fs, enc = wavread(args[0])

    #############################################
    #   Maintenance of all calculated energies
    #   and average energies:
    #############################################
    energy_spikes = []
    energy_averages = []
    energy_averages_SDs = []
    energies = []

    #############################################
    #   Iteration over sample packs of song:
    #############################################
    # static parameters
    SAMPLE_PACK_SIZE = int(256 / 2)
    ENERGY_HISTORY_SIZE = int((44100 * 1.3) / SAMPLE_PACK_SIZE)
    THRESHOLD_C = 1.3

    # contains the last <ENERGY_HISTORY_SIZE> energies
    energy_history = deque(maxlen=ENERGY_HISTORY_SIZE)


    start = int(len(amp_data) * 0.1)
    end = start + int(44100 * 60) # 15 seconds
    # cuts off the extra samples at the end.
    nthIndex = range(start, end - ((end - start) % SAMPLE_PACK_SIZE), SAMPLE_PACK_SIZE)

    for i in nthIndex:
        sample_pack = amp_data[i:i + SAMPLE_PACK_SIZE]

        # calculate the instance energy (squared) of this sample pack
        energy = tools.average(tools.squared(sample_pack), isLR=True)

        # append the instance energy to the right of the history list
        energy_history.append(energy)


        if len(energy_history) >= ENERGY_HISTORY_SIZE:
            # the history buffer is full so we can begin comparing average energy

            energies.append(energy)

            average_energy = tools.average(energy_history)
            #average_energy_SD = tools.standard_dev(energy_history, average_energy)
            average_energy_diff = tools.linear_dev(energy_history, average_energy)

            energy_averages.append(average_energy)
            energy_averages_SDs.append(average_energy_diff)

            #determined_thresh = average_energy * (THRESHOLD_C + 0.5 * average_energy_SD)
            determined_thresh = average_energy * 1.4 + 0.1 * average_energy_diff


            # print determined_C
            # check for energy spike
            if energy > determined_thresh:
                # we have an energy spike!
                energy_spikes.append(energy)
            else:
                # no spike
                energy_spikes.append(0)
    ######################################################################

    # period = int((60.0 / bpm) * 44100 / SAMPLE_PACK_SIZE)
    #
    BPMs = range(60, 200, 1)
    periods = [ int((60.0 / bpm) * 44100 / SAMPLE_PACK_SIZE) for bpm in BPMs]

    period_i, correlations = compute_beat_with_impulse_trains(energies, periods)

    BPM = BPMs[period_i]
    print "BPM: " + str(BPM)
    impulse_train = generate_impulse_train(periods[period_i], len(energy_spikes), 0.5)



    ######################################################################
    fig, axs = plt.subplots(nrows=2, ncols=1)

    x = BPMs
    y = correlations
    axs[0].bar(x, y, facecolor='b', alpha=0.5, linewidth=1, width=1)
    axs[0].set_ylabel('E_BPMs')
    axs[0].set_xlabel('BPM')

    x = range(0, len(energy_spikes))
    y = energy_spikes
    y2 = impulse_train
    # axs[1].scatter(x, y, marker="|")
    # axs[1].bar(x, y, color='g', linewidth=0)
    axs[1].plot(x, y, color='g', linewidth=1)
    axs[1].plot(x, y2, color='b', linewidth=1,  alpha=0.3)
    axs[1].set_ylabel('Energy')
    axs[1].set_xlabel('Frame')

    plt.savefig("../graphs/" + args[0].split('/')[-1] + "_graph.png")


if __name__ == "__main__":
    folder = "/home/damian/Music/Trance/"

    allFiles = [file for file in os.listdir(folder) if file.endswith(".wav")]

    for file in allFiles:
        print file
        #if "Foolskape - Counting.wav" in file:
        main([folder + file])

    #main(sys.argv[1:])
