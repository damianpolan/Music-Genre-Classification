

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

    packsize = 512
    dataset = []


    dbControl = database.Controller()

    genres = ['house', 'dubstep']
    trainingData = dbControl.getTrainingSet(genres, 4)

    ids_and_genres = []
    for genre in genres:
        for song_id in trainingData[genre]:
            ids_and_genres.append((song_id, genre))

    #iterating over all pulled songs
    for id_and_genre in ids_and_genres:
        featureDatas = dbControl.pullFeatureForSong("Feature_Centroid", id_and_genre[0],packsize)


    def onTrain(index):
        log.debug("onTrain: " + str(dataset[index]))

    def onValidate(index):
        log.debug("onValidate: " + str(dataset[index]))
        return True

    def onDoneTraining():
        log.debug("DONE TRAINING")

    eightFold = validation.CrossValidation(len(dataset), onTrain, onValidate, onDoneTraining, folds=8)
    hitRate = eightFold.performValidation(shuffle=True)
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

if __name__ == "__main__":
    main(sys.argv[1:])
