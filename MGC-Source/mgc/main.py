import sys
sys.path.append("/home/damian/Music-Genre-Classification/MGC-Source/")

import warnings
from database import DatabaseService
from training import CrossValidation, Validator
from learner import LearnerSVC
from learner import LearnerTensorFlow
from learner import LearnerMLP

from mgc.tools import logs
import pickle


def save_model(learner, features, genres):
    pickled_save_path = "/home/damian/Music-Genre-Classification/Classifiers/SVM_Latest.pickled"

    # set some meta paramaters
    learner.required_features = features
    learner.genres = genres

    # save the SVM to directory
    pickle.dump(learner, open(pickled_save_path, "wb"))


def create_trained_model():
    genres = [
        'classical',
        'jazz',
        # 'opera',
        # 'reggae',
        'rock',
        'house',
        'hip hop'
    ]
    required_features = [
        'Centroid_AVG',
        'Centroid_SD',
        'RollOff_AVG',
        'RollOff_SD',
        'Flux_AVG',
        'Flux_SD',
        'BPM',
        'Noise',
        'NoiseTwo'
    ]
    db_service = DatabaseService()
    training_set = db_service.get_training_set(genres, required_features, 100, verbose=True)
    learner = LearnerSVC()
    learner.fit(training_set)

    save_model(learner, features=required_features, genres=genres)


def main(argv):

    ####################################################
    #   Constants
    ####################################################

    songs_per_genre = 200

    # songs_per_genre -100
    # c, r, h, hh = %83.59
    # c, j, r, h, hh = %77.83

    genres = [
        'classical',
        'jazz',
        # 'opera',
        # 'reggae',
        'rock',
        'house',
        'hip hop'
    ]
    required_features = [
        'Centroid_AVG',
        'Centroid_SD',
        'RollOff_AVG',
        'RollOff_SD',
        'Flux_AVG',
        'Flux_SD',
        'BPM',
        'Noise',
        # 'NoiseTwo'
    ]

    ####################################################
    #   Training Set Fetch
    ####################################################

    db_service = DatabaseService()

    training_set = db_service.get_training_set(genres, required_features, songs_per_genre, verbose=True)

    cross_val = CrossValidation(training_set, k_folds=6)

    average_hit_rate = 0
    count = 0

    validator = Validator()
    for ts, vs in cross_val:
        learner = LearnerSVC()
        learner.fit(ts)
        results = validator.validate_next(learner, vs)

        average_hit_rate += results.hit_rate()
        count += 1.0
        print results

    print "Total samples: " + str(training_set.total_samples())
    print "Training/Validation: " + str(cross_val.training_size()) + " / " + str(cross_val.validation_size())
    print "Average hit rate: %" + "%.2f" % (100 * average_hit_rate / count)



if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        logs.enable_default_log()
        main(sys.argv[1:])
        # create_trained_model()
