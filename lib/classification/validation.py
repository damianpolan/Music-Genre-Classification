
import logging
import random

class CrossValidation():

    """
    Permorms an n fold validation technique.

    Reference:
        https://en.wikipedia.org/wiki/Cross-validation_(statistics)

    """

    def __init__(self, dataSetSize, onTrain, onValidate, onDoneTraining, folds=8):
        """
        trainingSetSize:    the length of the data. (i.e nubmer of sample packs analysed)
        onTrain(index):     function called when a training call is made. 
            - input: the data set index to train
            - No return value needed.

        onValidate(index):  function called when a validate call is made. 
            - input: the data set index to validate
            - Must return a boolean indicating if the classification was correct.

        onDoneTraining():  function called when the training phase is complete. Always happens before the first onValidate() call.
            - input: none
            - no return value

        folds:  The nubmer of folds to make. i.e: 8 folds -> 7 folds for training, 1 for validation
        """

        if dataSetSize <= 0:
            raise "Invalid dataSetSize. Must be greater than zero."

        self.dataSetSize = dataSetSize
        self.onTrain = onTrain
        self.onValidate = onValidate
        self.onDoneTraining = onDoneTraining
        self.folds = folds

    def performValidation(self, shuffle=True):
        """
        Runs the cross validation
        returns the hit rate.
        """
        crossover = self.dataSetSize - (self.dataSetSize / self.folds)

        indexes = range(0, self.dataSetSize)
        if shuffle:
            random.shuffle(indexes)

        # train
        for i in indexes[:crossover]:
            self.onTrain(i)

        self.onDoneTraining()

        # validate
        successCount = 0
        for i in indexes[crossover:]:
            success = self.onValidate(i)

            if not isinstance(success, bool):
                raise "onValidate() must return a boolean."

            if success:
                successCount += 1

        # calculate hit rate
        hitRate =  float(successCount / float(self.dataSetSize / self.folds))
        return hitRate



"""
EXAMPLE:    CrossValidation

def main(argv):
    dataset = range(1000, 2000)

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

"""