

import sys
import os
import logging as log
  
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from classification import algorithms 
from classification import validation 
from fingerprints import database
from fingerprints import tools


from sklearn import svm

def main(argv):
    tools.defaultLog()

    packsize = 512

    # dbControl = database.Controller()
    # dbControl.getTrainingSet(['trance', 'dubstep'], -1)

    dataset = range(1000, 2000)

    def onTrain(index):
        log.debug("onTrain: " + str(dataset[index]))

    def onValidate(index):
        log.debug("onValidate: " + str(dataset[index]))
        return index % 2 == 0

    eightFold = validation.CrossValidation(len(dataset), onTrain, onValidate, folds=8)

    hitRate = eightFold.performValidation(shuffle=True)
    log.debug("hitRate = " + str(hitRate))
    # machine = svm.SVC()
    # machine.fit(desc, classes)


    # desc = [ [1, 1], [11,11]]
    # classes = ['b', 'a']
    # machine.fit(desc, classes)


    # print machine.predict([3, 3])

    # classifier = SupportVectorCLS()

    #assign descriptors and classifications


    pass

if __name__ == "__main__":
    main(sys.argv[1:])