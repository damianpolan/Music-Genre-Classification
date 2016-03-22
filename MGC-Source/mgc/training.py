import sys
import abc
import random


####################################################
#   Training Set
####################################################

class TrainingSet:
    def __init__(self, classes, training_bins):
        self.classes = classes

        self.class_hash = {}
        self.__training_bin_length = len(training_bins[0])

        if self.__training_bin_length > 0:
            self.__numb_features = len(training_bins[0][0])
        else:
            self.__numb_features = -1 #unknown

        for i in range(len(classes)):
            self.class_hash[classes[i]] = training_bins[i]
            if len(training_bins[i]) != self.__training_bin_length:
                raise "All training bins must be the same length."

    def number_of_features(self):
        return self.__numb_features

    def training_bin_length(self):
        return self.__training_bin_length

    def get_XY(self):
        X = []
        Y = []
        # guarantees correct order
        for class_name, training_set in self.class_hash.iteritems():
            for features in training_set:
                X.append(features)
                Y.append(class_name)
        return X, Y

    def total_samples(self):
        total = 0
        for class_name, bin in self.class_hash.iteritems():
            total += len(bin)
        return total

    def shuffle(self):
        """
        Shuffles each training bin randomly
        :return:
        """
        for class_name in self.classes:
            random.shuffle(self[class_name])

    def subset(self, start, end):

        new_training_bins = []
        new_classes = []

        for class_name, training_bin in self.class_hash.iteritems():
            new_training_bins.append(training_bin[start:end])
            new_classes.append(class_name)

        return TrainingSet(new_classes, new_training_bins)

    def __add__(self, other):
        new_training_bins = []
        new_classes = []

        for class_name in self.class_hash:
            curr_bin = self.class_hash[class_name]
            curr_bin.extend(other[class_name])

            new_training_bins.append(curr_bin)
            new_classes.append(class_name)

        return TrainingSet(new_classes, new_training_bins)

    def __getitem__(self, class_name):
        return self.class_hash[class_name]


class ValidationResults:
    """
    Holds the results of a validator validation run.
    """
    def __init__(self, classes, name):
        self.name = name
        self.total = 0
        self.hits = 0
        self.results = dict()
        for expected in classes:
            self.results[expected] = dict()
            for predicted in classes:
                self.results[expected][predicted] = 0

    def add_result(self, predicted, expected):
        self.total += 1
        if predicted == expected:
            self.hits += 1
        self.results[expected][predicted] += 1

    def hit_rate(self, class_name=None):
        if class_name:
            total = 0
            hits = self.results[class_name][class_name]
            for pred in self.results[class_name]:
                total += self.results[class_name][pred]
            return hits / float(total)
        else:
            return self.hits / float(self.total)

    def __str__(self, show_predicted=False):
        newln = "\n"
        tb = "\t"
        strn = ""

        strn += self.name + newln
        strn += 'hits: ' + str(self.hits) + '/' + str(self.total) + ' - ' + str("%.3f" % self.hit_rate()) + newln

        for expected in self.results:
            strn += tb + str(expected) + ' - ' + str("%.2f" % self.hit_rate(expected)) + newln
            if show_predicted:
                strn += tb + tb + str(expected) + ': ' + str(self.results[expected][expected]) + newln
                for predicted in self.results:
                    if predicted != expected:
                        strn += tb + tb + str(predicted) + ': ' + str(self.results[expected][predicted]) + newln

        return strn


class Validator:

    def __init__(self):
        self.count = 0

    def validate_next(self, learner, validation_set):
        self.count += 1

        X, Y = validation_set.get_XY()

        stats = ValidationResults(validation_set.classes, 'Test ' + str(self.count))

        for i in range(len(X)):
            expected = Y[i]
            predicted = learner.predict(X[i])
            stats.add_result(predicted, expected)

        return stats


####################################################
#   Abstract Classes
####################################################

class ValidationTechnique:
    __metaclass__ = abc.ABCMeta

    def __init__(self, training_set):
        """
        :param TrainingSet object
        """
        self.training_set = training_set

    @abc.abstractmethod
    def __iter__(self):
        """
        Returns the next training and validation set.
        :return: If the next set is available the function returns a tuple:
            ( TrainingSet object for training samples, TrainingSet object for validation samples )
            Otherwise, returns None
        """
        return

    @abc.abstractmethod
    def next(self):
        """
        Returns the next training and validation set.
        :return: If the next set is available the function returns a tuple:
            ( TrainingSet object for training samples, TrainingSet object for validation samples )
            Otherwise, returns None
        """
        return


####################################################
#   Concrete Implementations
####################################################

class CrossValidation(ValidationTechnique):

    def __init__(self, training_set, k_folds):
        """
        :param k_folds: The number of folds to perform
        :return:
        """
        ValidationTechnique.__init__(self, training_set)
        self.k_folds = k_folds

        ts = self.training_set
        ts.shuffle()

        self.training_sets = []
        self.validation_sets = []

        fold_size = ts.training_bin_length() / self.k_folds
        # i = 0
        # 0 - 2, 2 - (-1)

        for i in range(0, k_folds):
            l1 = i * fold_size

            l2 = l1 + fold_size
            if i >= k_folds - 1: # for odd divisions, the last fold goes all the way to the end.
                l2 = ts.training_bin_length()

            validation = ts.subset(l1, l2)
            training = ts.subset(0, l1) + ts.subset(l2, None)
            self.training_sets.append(training)
            self.validation_sets.append(validation)

    def training_size(self):
        return self.training_sets[0].training_bin_length() * len(self.training_sets[0].classes)

    def validation_size(self):
        return self.validation_sets[0].training_bin_length() * len(self.validation_sets[0].classes)

    def __iter__(self):
        self.iter_index = 0
        return self

    def next(self):
        if self.iter_index < len(self.training_sets):
            next_tv = (self.training_sets[self.iter_index], self.validation_sets[self.iter_index])
            self.iter_index += 1
            return next_tv
        else:
            raise StopIteration


def main(argv):
    ts = TrainingSet(("A", "B"),
                     [
                         [ ["f1x", "f2", "f3"], ["f1y", "f2", "f3"], ["f1z", "f2", "f3"]
                             , ["f1a", "f2", "f3"], ["f1b", "f2", "f3"], ["f1c", "f2", "f3"]
                             , ["f1d", "f2", "f3"], ["f1e", "f2", "f3"], ["f1f", "f2", "f3"]],
                         [ ["f1x", "f2", "f3"], ["f1y", "f2", "f3"], ["f1z", "f2", "f3"]
                             , ["f1a", "f2", "f3"], ["f1b", "f2", "f3"], ["f1c", "f2", "f3"]
                             , ["f1d", "f2", "f3"], ["f1e", "f2", "f3"], ["f1f", "f2", "f3"]]
                     ])


    cv = CrossValidation(ts, 3)

    for training_set, validation_set in cv:
        i = 0

if __name__ == "__main__":
    main(sys.argv[1:])