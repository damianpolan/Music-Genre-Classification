
import logging
import random

class HoldOutValidation():

    """
    Performs a Hold out validation technique.

    Notes:
    - the percent hit rate calculation is limiting here as their is no ability to calculate false positive and true negatives rates.

    """

    def __init__(self, dataSetSize, onTrain, onValidate, onDoneTraining, validationPercent=0.15):
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
        self.validationPercent = validationPercent


    def performValidation(self, shuffle=True, divide=1):
        """
        Runs the cross validation
        returns the hit rate.
        :param shuffle: Whether to shuffle the data randomly (applied after divide)
        :param divide: divide >= 1 will divide the set indexes into divide # bins and pick randomly evenly from each one.

        The training set will pull an equal amount of training data from each bin. This prevents a bias from occurring
        when more of one genre is used to train.
        Requirements:
            The divide parameter should be = number of genres
            The data set should be arranged as followed (for divide = 3):
                [ .. x house .. , .. x trance .., x dubstep .. ]
            The number of training samples for each should be x. I.e all the same.
            If these are all met the training set should be evenly divisible by divide.

        :return:
        """
        # the indexes mapping to the external data set
        indexes = range(0, self.dataSetSize)

        # split the indexes into a number of bins (divide) and shuffle if shuffle=True
        bins = []
        binSize = int(self.dataSetSize / divide)
        for i in range(0, divide):
            newBin = indexes[i * binSize:i * binSize + binSize]
            if shuffle:
                random.shuffle(newBin)
            bins.append(newBin)

        crossover = int(binSize * (1 - self.validationPercent))


        # train
        for bin in bins:
            for i in bin[:crossover]:
                self.onTrain(i)

        self.onDoneTraining()

        # validate
        successCount = 0
        for bin in bins:
            for i in bin[crossover:]:
                success = self.onValidate(i)

                if not isinstance(success, bool):
                    raise "onValidate() must return a boolean value."

                if success:
                    successCount += 1

        # calculate hit rate
        hitRate = float(successCount / float(self.dataSetSize * self.validationPercent))
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