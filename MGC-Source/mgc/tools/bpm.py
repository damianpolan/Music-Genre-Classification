
import math
import numpy as np
import pcm
import stats
from collections import deque


def correlation_energy(wav1, wav2):
    """
    Determines the similarity between two waves using sum of products.
    """
    correlation_e = 0
    for k in range(0, len(wav1)):
        correlation_e += abs(wav1[k] * wav2[k])

    return correlation_e


def mean_squared_error(wav1, wav2):
    """
    Determines the similarity between two waves using mean squared error.
    """
    summ = 0
    for k in range(len(wav1)):
        summ += (wav1[k] - wav2[k]) ** 2

    mean_squared_e = summ / len(wav1)
    return mean_squared_e


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
    return impulse_train


def compute_beat_with_impulse_trains(wave, periods):
    """
    Uses an impulse train comparison to determine the beat period of a signal.
    :param wave:
    :param periods: the beat periods to check
    :return: the index of periods which is the closes match
    """
    N = len(wave)
    wav_fft = np.fft.fft(wave)[0:N / 2]  # remove repeated FFT information

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
    c = 4  # area around i to average
    largest_i_area = 0
    largest_i = 0
    for i in range(0, len(correlations)):
        # wierd max here.
        v_curr, x = stats.avg_around_index(i, c, correlations)
        v_larg, x1n = stats.avg_around_index(largest_i_area, c, correlations)

        if  v_curr >= v_larg:
            largest_i_area = i
            largest_i = x

    # return largest_i_area... wierd but gives better results
    return largest_i_area, correlations


def compute_best_fit_line(data):
    """
    Computs the line of best fit for a list of values. Assumes x value is the index of the item in the list.
    http://hotmath.com/hotmath_help/topics/line-of-best-fit.html
    :param data: list of data points
    :return: (m, b) or .. (slope, yoffset)
    """
    avg_x = len(data) / 2
    avg_y = stats.average(data)
    xXyY = 0
    xX2 = 0

    for x in range(len(data)):
        xXyY += (x - avg_x) * (data[x] - avg_y)
        xX2 += math.pow(x - avg_x, 2)

    slope_m = xXyY / xX2
    yoffet_b = avg_y - slope_m * avg_x
    return slope_m, yoffet_b


def pearsons_product_moment(wavx, wavy):
    """
    https://en.wikipedia.org/wiki/Correlation_and_dependence
    :param wav1:
    :param wav2:
    :return:
    """
    avg_x = stats.average(wavx)
    avg_y = stats.average(wavy)

    xXyY = 0
    xX2 = 0
    yY2 = 0

    for i in range(len(wavx)):
        xXyY += (wavx[i] - avg_x) * (wavy[i] - avg_y)
        xX2 += math.pow(wavx[i] - avg_x, 2)
        yY2 += math.pow(wavy[i] - avg_y, 2)

    r = xXyY / (math.sqrt(xX2 * yY2))
    return r


def determine_bpm(pcm_data):

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

    start = 0 # int(len(pcm_data) * 0.1)
    end = start + int(44100 * 120)  # 60 seconds
    end = min(end, len(pcm_data))
    # cuts off the extra samples at the end.
    nthIndex = range(start, end, SAMPLE_PACK_SIZE)

    for i in nthIndex:
        sample_pack = pcm_data[i:i + SAMPLE_PACK_SIZE]

        if len(sample_pack) != SAMPLE_PACK_SIZE:
            continue

        # calculate the instance energy (squared) of this sample pack
        energy = stats.average(stats.squared(sample_pack))

        # append the instance energy to the right of the history list
        energy_history.append(energy)

        if len(energy_history) >= ENERGY_HISTORY_SIZE:
            # the history buffer is full so we can begin comparing average energy

            energies.append(energy)

            average_energy = stats.average(energy_history)
            average_energy_diff = stats.linear_dev(energy_history, average_energy)

            energy_averages.append(average_energy)
            energy_averages_SDs.append(average_energy_diff)

            determined_thresh = average_energy * 1.4 + 0.1 * average_energy_diff

            # print determined_C
            # check for energy spike
            if energy > determined_thresh:
                # we have an energy spike!
                energy_spikes.append(energy)
            else:
                # no spike
                energy_spikes.append(0)

    BPMs = range(60, 200, 1)
    periods = [int((60.0 / bpm) * 44100 / SAMPLE_PACK_SIZE) for bpm in BPMs]

    period_i, correlations = compute_beat_with_impulse_trains(energies, periods)

    bpm = BPMs[period_i]

    return bpm

