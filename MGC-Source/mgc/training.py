import abc


####################################################
#   Trainer Abstract Class
####################################################

class TrainingSet:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        return

    @abc.abstractmethod
    def get_training_set(self):
        return

    @abc.abstractmethod
    def get_validation_set(self):
        return

####################################################
#   Trainer Concrete Implementations
####################################################

class SimpleSet


