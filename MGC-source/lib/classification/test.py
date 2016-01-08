

import sys
import os
import logging as log

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

    genres = ['dubstep', 'trance', 'house']
    training_data = dbControl.getTrainingSet(genres, 40) #40

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

        # featureDatas will contain an array of feature objects
        feature_data_centroid = dbControl.pullFeatureForSong("Feature_Centroid_Avg", id_and_genre[0],packsize)
        feature_data_rolloff = dbControl.pullFeatureForSong("Feature_Rolloff_Avg", id_and_genre[0],packsize)

        # log.debug("feature_datas.length = " + str(len(feature_datas)))
        # take 200 samples from the middle-ish
        #for i in range(2000, 2200):
        centroid = float(feature_data_centroid[0].value)
        rolloff = float(feature_data_rolloff[0].value)
        samples.append((centroid, rolloff))
        classes.append(id_and_genre[1])
        log.debug("@@@@" + id_and_genre[1] + "  centroid=" + str(centroid) + " rolloff=" + str(rolloff))

    machine = svm.SVC(C=1.0, kernel='linear', degree=4)

    training_indexes = []

    def onTrain(index):
        training_indexes.append(index);

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

        machine.fit(chosen_samples, chosen_classes)
        log.debug("Fitting.")

    holdOut = validation.HoldOutValidation(len(samples), onTrain, onValidate, onDoneTraining, validationPercent=0.2)

    # the divide should be the number of genres. An equal amount of samples must be trained from each genre
    hitRate = holdOut.performValidation(shuffle=True, divide=len(genres))
    log.debug("hitRate = " + str(hitRate))

    # machine = svm.SVC()
    # machine.fit(desc, classes)

    # desc = [ [1, 1], [11,11]]
    # classes = ['b', 'a']
    # machine.fit(desc, classes)

    # print machine.predict([3, 3])

    # classifier = SupportVectorCLS()

    # assign descriptors and classifications

    pass

import warnings
if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        main(sys.argv[1:])
