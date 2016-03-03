import tools
import math
import numpy as np

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
        sum += math.pow(wav1[k] - wav2[k], 2)

    mean_squared_e = sum / len(wav1)
    return  mean_squared_e

def generate_impulse_train(period, size, amplitude=1000):
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
    :return: The beat period (can be converted directly to BPM)
    """
    N = len(wave)
    wav_fft = np.fft.fft(wave)[0:N / 2] # remove repeated FFT information

    correlations = []
    for period in periods:
        impulse_train = generate_impulse_train(period, N)
        impulse_train_fft = np.fft.fft(impulse_train)
        correlation = mean_squared_error(wav_fft, impulse_train_fft)
        correlations.append(correlation)

    largest_i = 0
    for i in range(len(correlation)):
        if correlation[i] > correlation[largest_i]:
            largest_i = i

    determined_period = periods[largest_i]

    return  determined_period





def main(argv):
    pass


if __name__ == "__main__":
    main(sys.argv[1:])
