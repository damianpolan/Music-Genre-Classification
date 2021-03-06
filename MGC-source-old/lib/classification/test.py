

import sys
import os
import logging as log
import pickle
import numpy as np


sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from classification import algorithms
from classification import validation
from fingerprints import database
from fingerprints import tools


# testing imports
from sklearn import svm

# neural networks
# http://scikit-neuralnetwork.readthedocs.org/en/latest/guide_installation.html
# from sknn.mlp import Classifier as NN_Classifier
#from sknn.mlp import Layer
import sknn.mlp as mlp


def main(argv):
    tools.defaultLog()


    """
        packsize = 1024 --> about 42 sample packs per second
    """

    packsize = 1024
    dataset = []

    dbControl = database.Controller()

    required_features = [
        "Feature_Centroid_Avg",
        "Feature_Centroid_SD",
        "Feature_Rolloff_Avg",
        "Feature_Rolloff_SD",
        "Feature_Flux",
        "Feature_Spec_Flux_Avg",
        "Feature_Spec_Flux_SD"
    ]

    genres = [
        'dubstep',
        'house',
        'trance'
    ]

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

        samples.append(np.array(features))
        classes.append(id_and_genre[1])

    machine = svm.SVC(C=1.0, kernel='poly', degree=2, shrinking=True, verbose=False)
    # machine = mlp.Classifier(
    #         layers=(mlp.Layer("Sigmoid", units=4),
    #                 mlp.Layer("Linear", units=len(genres))),
    #         learning_rate=0.02,
    #         n_stable=200)


    training_indexes = []
    hitRates = {}

    def onTrain(index):
        training_indexes.append(index)

    def onValidate(index):

        predicted = machine.predict(np.array([samples[index]]))[0]
        expected = classes[index]

        is_valid = (predicted == expected)

        if not hitRates.has_key(expected):
            hitRates[expected] = {}
            hitRates[expected]["total"] = 0
            hitRates[expected]["correct"] = 0

        hitRates[expected]["total"] += 1


        if predicted == expected:
            hitRates[expected]["correct"] += 1
        else:
            if not hitRates[expected].has_key(predicted):
                hitRates[expected][predicted] = 0
            hitRates[expected][predicted] += 1

        log.debug(str(is_valid) + "  \t got " + str(predicted) + " expected " + str(expected))
        return is_valid

    def onDoneTraining():
        chosen_samples = []
        chosen_classes = []
        for i in training_indexes:
            chosen_samples.append(samples[i])
            chosen_classes.append(classes[i])

        X = np.array(chosen_samples)
        Y = np.array(chosen_classes)

        log.debug("Fitting ...")
        machine.fit(X, Y)

    holdOut = validation.HoldOutValidation(len(samples), onTrain, onValidate, onDoneTraining, validationPercent=0.2)

    # the divide should be the number of genres. An equal amount of samples must be trained from each genre
    hitRate = holdOut.performValidation(shuffle=False, divide=len(genres))
    log.debug("hitRate = " + str(hitRate))

    for genre, v in hitRates.iteritems():
        log.debug(str(genre).upper() + ": " + str(v["correct"]) + "/" + str(v["total"]))
        for hitg, amount in v.iteritems():
            if hitg not in ["correct", "total"]:
                log.debug("\t\t" + str(hitg) + "= " + str(amount))

    pickled_save_path = "/home/damian/Music-Genre-Classification/Classifiers/SVM_Latest.pickled"

    # set some meta paramaters
    machine.required_features = required_features
    machine.pack_size = packsize
    machine.genres = genres

    # save the SVM to directory
    # pickle.dump(machine, open( pickled_save_path, "wb" ) )


import warnings

if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        main(sys.argv[1:])
