
import numpy as np


def to_sample_packs(pcm_data, sample_pack_size):
    for i in range(0, len(pcm_data) - sample_pack_size, sample_pack_size):
        yield pcm_data[i:pcm_data + sample_pack_size]


def into_mono(sample_pack):
    """
     data = time domain data in list format. Each element in the list should be an array of length two with each subelement being the left/right (stereo) sample.

    output:
        list of sample data in mono format. Each element is the sum of the left/right sample
    :param sample_pack:
    :return:
    """
    return [pair[0] + pair[1] for pair in sample_pack]


def into_freq_domain(pcm_data):
    # into frequency domain, takes the magnitutde of the complex
    if isinstance(pcm_data[0], list):
        # in stereo format
        if len(pcm_data[0]) != 2:
            raise "Must be list of length 2. For left and right speakers."

        fft = np.fft.fft(pcm_data)
        fft = fft[0:len(fft) / 2]
        return [[abs(pair[0]), abs(pair[1])] for pair in fft]
    else:
        # in mono format
        fft = np.fft.fft(pcm_data)
        fft = fft[0:len(fft) / 2] # we remove the last half of the data (the -ve frequencies).
        return [abs(element) for element in fft]


def frequency_at_fft_index(bin_index, fft_length, sample_rate_hz=44100):
    """
    Calculates the frequency of the given bin in a FFT result (frequency domain).

    binIndex        The index of the bin to get the frequency for.
    fftLength       The length of the frequency domain list data.
    sampleRateHz:   The sample rate of the audio.

    returns:
        The frequency of the bin. = (binIndex * (sampleRateHz / 2) / fftLength)

    :param bin_index:
    :param fft_length:
    :param sample_rate_hz:
    :return:
    """

    return bin_index * (sample_rate_hz / 2.0) / float(fft_length)


def centroid(pcm_data):
    """
    Calculates the centroid of a given sample pack.
    centroid = sum(f * M(f)) / sum (M(f))
    :param pcm_data: time domain data
    :return: centroid value as float
    """
    freq_data = into_freq_domain(into_mono(pcm_data))

    sum_fm = 0
    sum_m = 0
    for cbin in range(0, len(freq_data)):
        f = frequency_at_fft_index(cbin, len(freq_data))
        sum_fm += f * freq_data[cbin]  # f * M(f)
        sum_m += freq_data[cbin]  # M(f)

    # handle the divide by zero case!
    if sum_m != 0:
        centr = sum_fm / sum_m
    else:
        centr = 0

    return centr
