import abc

####################################################
#   Learner Abstract Class
####################################################

class Learner:
    __metaclass__ = abc.ABCMeta

    def __init__(self):

    @abc.abstractmethod
    def fit(self):
        return

    @abc.abstractmethod
    def classify(self):
        return

