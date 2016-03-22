import abc
from sklearn import svm
import tensorflow as tf
import sknn.mlp as mlp
import numpy as np


####################################################
#   Learner Abstract Class
####################################################

class Learner:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        return

    @abc.abstractmethod
    def fit(self, training_set):
        return

    @abc.abstractmethod
    def predict(self, features):
        return


####################################################
#   Concrete Implementations
####################################################

class LearnerSVC(Learner):
    """
    http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html

    SVC guide:
    http://tdlc.ucsd.edu/events/boot_camp_2009/tingfansvm.pdf
    :return:
    """
    def __init__(self):

        self.machine = svm.SVC(
                C=1.1, kernel='linear', degree=2, gamma='auto',
                coef0=1.0, shrinking=True, probability=False,
                tol=1e-3, cache_size=200, class_weight=None,
                verbose=False, max_iter=-1, decision_function_shape=None,
                random_state=None)
        return

    def fit(self, training_set):
        X, Y = training_set.get_XY()
        self.machine.fit(X, Y)

    def predict(self, features):
        return self.machine.predict(features)[0]


class LearnerTensorFlow(Learner):

    def __init__(self, numb_features, number_classes):
        # allows us to input any number of samples
        # each sample has two features
        self.x = tf.placeholder(tf.float32, [None, numb_features])

        # we are going to learn W and b
        W = tf.Variable(tf.zeros([numb_features, number_classes]))
        b = tf.Variable(tf.zeros([number_classes]))

        # y is predicted probability distribution
        # this is our actual model.
        self.y = tf.nn.softmax(tf.matmul(self.x, W) + b)

        # y' (y_) is the true distribution. (The one-hot vector we will input)
        # y_ is a placeholder to input the correct answers
        self.y_ = tf.placeholder(tf.float32, [None, number_classes])

        # cross entropy measures how inefficient our predictions are for describing the truth
        # this isn't just the cross-entropy of the truth with a single prediction,
        # but the sum of the cross-entropies for all the images we looked at
        cross_entropy = -tf.reduce_sum(self.y_*tf.log(self.y))

        # we ask TensorFlow to minimize cross_entropy using the gradient descent algorithm
        self.train_step = tf.train.GradientDescentOptimizer(0.01).minimize(cross_entropy)

        init = tf.initialize_all_variables()
        self.sess = tf.Session()
        self.sess.run(init)


    def fit(self, training_set):
        X, Y = training_set.get_XY()

        self.class_map = dict()
        counter = 0
        # convert class names
        for class_name in Y:
            if class_name not in self.class_map:
                self.class_map[class_name] = counter
                counter += 1

        for key, val in self.class_map.iteritems():
            self.class_map[key] = [0] * counter
            self.class_map[key][val] = 1

        batch_ys = []
        for y in Y:
            batch_ys.append(self.class_map[y])

        batch_xs = X
        self.sess.run(self.train_step, feed_dict={self.x: batch_xs, self.y_: batch_ys})

    def predict(self, features):
        feed_dict = { self.x: [features]}
        classification = self.sess.run(self.y, feed_dict)[0]

        for key, val in self.class_map.iteritems():
            if list(classification) == val:
                return key

        raise "Something went wrong. The classigication was not found in the class_map?"


class LearnerMLP(Learner):

    def __init__(self, numb_classes):
        self.machine = mlp.Classifier(
            layers=(mlp.Layer("Sigmoid", units=numb_classes),),
            learning_rate=0.001)

    def fit(self, training_set):
        X, Y = training_set.get_XY()
        self.machine.fit(np.array(X), np.array(Y))

    def predict(self, features):
        result = self.machine.predict(np.array([features]))[0][0]
        return result


