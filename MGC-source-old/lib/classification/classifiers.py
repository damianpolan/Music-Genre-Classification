class SupervisedClassifier:
    """
    Classifies a single pack of data.

    """


    def __init__(self):
        raise "Not implemented"
    

    def fit(self, descriptors, classes):
        """
        Supervised training fitting the given feature descriptors to the target.

        @param descriptors: The list of training vectors to fit.
        @param classes: Target classifications of the training vectors.

        descriptors format:
        [
            [ all descriptors for 1],
            [ all descriptors for 2],
            ...
            [ all descriptors for n]
        ]

        classes format:
        [
            classification for 1,
            classification for 2,
            ...
            classification for n
        ]


        """
        raise "Not implemented"


    def classify(self, item):
        raise "Not implemented"





