

from classifiers import SupervisedClassifier
from sklearn import svm

class SupportVectorCLS(SupervisedClassifier):

    def __init__(self):
        self.classifier = svm.SVC()
    

    def fit(self, descriptors, classes):
        """
        descriptors format:
        [
            [ all descriptors for 1],
            [ all descriptors for 2],
            ...
            [ all descriptors for n]
        ]

        classes format:
        [   classification for 1,
            classification for 2,
            ...
            classification for n ]
        """

        self.classifier.fit(descriptors, classes)


    def classify(self, descriptors):
        self.classifier.predict(descriptors)

    pass