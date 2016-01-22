

import sys
import os
import logging as log
import pickle

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from classification import algorithms
from classification import validation
from fingerprints import database
from fingerprints import tools


# testing imports
from sklearn import svm


def main(argv):
    tools.defaultLog()

    """
        packsize = 1024 --> about 42 sample packs per second
    """

    packsize = 1024
    dataset = []

    dbControl = database.Controller()

    required_features = ["Feature_Centroid_Avg", "Feature_Centroid_SD", "Feature_Rolloff_Avg", "Feature_Rolloff_SD"]
    genres = ['dubstep', 'house', 'trance']
    training_data = dbControl.getTrainingSet(genres, 40)

    ids_and_genres = []
    print training_data
    for genre in genres:
        for song_id in training_data[genre]:
            ids_and_genres.append((song_id, genre))

    samples = []
    classes = []
    # iterating over all pulled songs
    for id_and_genre in ids_and_genres:
        log.debug("Fetching " + str(id_and_genre))

        features = []
        for feat in required_features:
            features.append(dbControl.pullFeatureForSong(feat, id_and_genre[0],packsize)[0].value)

        samples.append(tuple(features))
        classes.append(id_and_genre[1])

    machine = svm.SVC(C=1.0, kernel='linear', degree=2)

    training_indexes = []

    def onTrain(index):
        training_indexes.append(index)

    def onValidate(index):
        predicted = machine.predict(samples[index])[0]
        expected = classes[index]
        is_valid = (predicted == expected)
        log.debug(str(is_valid) + "  \t got " + predicted + " expected " + expected)
        return is_valid

    def onDoneTraining():
        chosen_samples = []
        chosen_classes = []
        for i in training_indexes:
            chosen_samples.append(samples[i])
            chosen_classes.append(classes[i])


        log.debug("Fitting ...")
        machine.fit(chosen_samples, chosen_classes)

    holdOut = validation.HoldOutValidation(len(samples), onTrain, onValidate, onDoneTraining, validationPercent=0.2)

    # the divide should be the number of genres. An equal amount of samples must be trained from each genre
    hitRate = holdOut.performValidation(shuffle=True, divide=len(genres))
    log.debug("hitRate = " + str(hitRate))




    pickled_save_path = "/home/damian/Music-Genre-Classification/Classifiers/SVM_Latest.pickled"
    machine.required_features = required_features

    # save the SVM to directory
    pickle.dump(machine, open( pickled_save_path, "wb" ) )


import warnings
if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        main(sys.argv[1:])
