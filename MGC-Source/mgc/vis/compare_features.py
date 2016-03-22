import sys
import matplotlib.pyplot as plt
import matplotlib.colors as mcs
from mgc.database import DatabaseService
import numpy as np
from mgc.learner import LearnerSVC
import mgc.tools.pcm as pcm
from scikits.audiolab import wavread


def plot_compare(genres, features, training_set, n=800, out_file=None):

    fig, axs = plt.subplots(nrows=1, ncols=1)

    for genre in genres:
        feature_set = training_set[genre]

        x = [feat[0] for feat in feature_set]
        y = [feat[1] for feat in feature_set]

        axs.plot(x, y, '.', ms=3, alpha=0.8, label=genre, antialiased=False)

    axs.set_xlabel(features[0])
    axs.set_ylabel(features[1])
    axs.legend()

    file_path = out_file or 'graphs/scatter_' + features[0] + '-' + features[1] + '_' + str(len(genres)) + '.png'
    print file_path
    plt.savefig(file_path)


def plot_compare_SVC(genres, features, training_set, SVC, out_file=None):


    Z = np.ndarray(shape=(10,10), dtype=float)
    Z.fill(0.0)

    # create a mesh to plot in
    f_X = []
    f_Y = []
    for genre in genres:
        f_X.extend(training_set[genre])
        for i in range(0, len(training_set[genre])):
            f_Y.append(genre)

    min_0, max_0 = f_X[0][0], f_X[0][0]
    min_1, max_1 = f_X[0][1], f_X[0][1]

    for f0, f1 in f_X:
        min_0 = min(f0, min_0)
        min_1 = min(f1, min_1)
        max_0 = max(f0, max_0)
        max_1 = max(f1, max_1)

    min_0 -= (max_0 - min_0) * 0.1
    max_0 += (max_0 - min_0) * 0.1
    min_1 -= (max_1 - min_1) * 0.1
    max_1 += (max_1 - min_1) * 0.1

    step_size_0 = (max_0 - min_0) / 1000.0
    step_size_1 = (max_1 - min_1) / 1000.0

    xx, yy = np.meshgrid(np.arange(min_0, max_0, step_size_0),
                         np.arange(min_1, max_1, step_size_1))

    fig, axs = plt.subplots(nrows=1, ncols=1)

    Z = SVC.machine.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    Z[Z == 'classical'] = 0.1
    Z[Z == 'jazz'] = 1.1
    Z[Z == 'hip hop'] = 2.1
    Z[Z == 'house'] = 3.1
    Z[Z == 'rock'] = 4.1

    levels = [0, 1, 2, 3, 4, 5]
    CS = plt.contourf(xx, yy, Z, alpha=0.2, levels=levels,
                      colors=('b', 'g', 'm', 'c', 'r'))

    for genre in genres:
        feature_set = training_set[genre]

        x = [feat[0] for feat in feature_set]
        y = [feat[1] for feat in feature_set]

        axs.plot(x, y, '.', ms=4, alpha=0.9, label=genre, antialiased=False)

    axs.set_xlabel(features[0])
    axs.set_ylabel(features[1])
    axs.legend()

    file_path = 'graphs/SVC_' + features[0] + '-' + features[1] + '.png'
    print file_path
    plt.savefig(file_path)


def compare_two_songs_pcm(pcm1, pcm2, features):
    pass


def one_song_fft(pcm1, song_name, subset=None):
    # fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(10, 4))
    fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]}, figsize=(10, 6))

    pcm1 = pcm.into_mono(pcm1)[0:len(pcm1) / 2]

    if subset:
        pcm1 = pcm1[subset[0]: subset[1]]

    x = [i / 44100.0 for i in range(0, len(pcm1))]
    y = pcm1

    axs[0].plot(x, y, color='#006600', lw=0.05, antialiased=True)
    axs[0].set_ylabel("Amplitude")
    axs[0].set_xlabel("Time (Seconds)")

    fft = np.fft.fft(pcm1)
    fft = fft[0:len(fft)/2]
    x = [pcm.frequency_at_fft_index(i, len(fft)) for i in range(0, len(fft))]

    axs[1].set_ylim([-30000, 30000])
    axs[1].set_xlim([0, 22000])
    axs[1].plot(x, fft, color='#cc0000', lw=0.1, antialiased=True)
    axs[1].set_ylabel("Amplitude")
    axs[1].set_xlabel("Frequency (Hz)")

    fig.tight_layout()

    if subset:
        file_path = 'graphs/one_song_fft_' + song_name + '_subset' + '.png'
    else:
        file_path = 'graphs/one_song_fft_' + song_name + '.png'
    print file_path
    plt.savefig(file_path)

def one_song_fft_sub(pcm1, song_name, subset):

    fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]}, figsize=(10, 6))

    pcm1 = pcm.into_mono(pcm1)[0:len(pcm1) / 2]

    pcm1 = pcm1[subset[0]: subset[1]]

    x = [i / 44100.0 for i in range(0, len(pcm1))]
    y = pcm1

    # insert zeros
    i = 0
    while i < len(x):
        x.insert(i, 0.0)
        i += 2

    axs[0].plot(x, y, color='#006600', lw=1)
    # axs[0].bar(x, y, color='#006600', width=0.00001, linewidth=0)
    axs[0].set_ylabel("Amplitude")
    axs[0].set_xlabel("Time (Seconds)")

    fft = np.fft.fft(pcm1)
    fft = fft[0:len(fft)/2]
    x = range(0, len(fft))

    # axs[1].set_ylim([-30000, 30000])
    # axs[1].set_xlim([0, 22000])
    axs[1].bar(x, fft, color='#cc0000', antialiased=True)
    axs[1].set_ylabel("Amplitude")
    axs[1].set_xlabel("Frequency Index")

    fig.tight_layout()

    file_path = 'graphs/one_song_fft_' + song_name + '_subset' + '.png'
    print file_path
    plt.savefig(file_path)


def main(argv):
    # for SVC plotting: http://scikit-learn.org/stable/auto_examples/svm/plot_iris.html
    genres = [
        'classical',
        'jazz',
        # 'opera',
        # 'reggae',
        'rock',
        'house',
        'hip hop'
    ]
    features = [
        'Centroid_AVG',
        'Centroid_SD',
        # 'RollOff_AVG',
        # 'RollOff_SD',
        # 'Flux_AVG',
        # 'Flux_SD',
        # 'BPM',
        # 'Noise',
        # 'NoiseTwo'
    ]

    print "retrieving"
    db_service = DatabaseService()
    training_set = db_service.get_training_set(genres, features, 100)

    print "training"
    learner = LearnerSVC()
    learner.fit(training_set)

    print "plotting"
    # plot_compare(genres, features, training_set)
    plot_compare_SVC(genres, features, training_set, learner)



    # pcm_data, fs, enc = wavread("/home/damian/Music/Dubstep/Elite Sync Lab - Oracle.wav")
    # one_song_fft(pcm_data, "Elite Sync Lab - Oracle")
    # one_song_fft_sub(pcm_data, "Elite Sync Lab - Oracle", subset=(100000, 102000))



if __name__ == "__main__":
    main(sys.argv[1:])
