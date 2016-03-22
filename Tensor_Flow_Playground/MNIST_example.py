import sys
from tensorflow.examples.tutorials.mnist import input_data
import tensorflow as tf
import numpy as np

def main(argv):
    # https://www.tensorflow.org/versions/r0.7/tutorials/mnist/beginners/index.html

    mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)


    x = tf.placeholder(tf.float32, [None, 784]) # allows us to input any number of mnist images

    # we are going to learn W and b
    W = tf.Variable(tf.zeros([784, 10]))
    b = tf.Variable(tf.zeros([10]))

    # y is predicted probability distribution
    # this is our actual model.
    y = tf.nn.softmax(tf.matmul(x, W) + b)

    # y' (y_) is the true distribution. (The one-hot vector we will input)
    # y_ is a placeholder to input the correct answers
    y_ = tf.placeholder(tf.float32, [None, 10])

    # cross entropy measures how inefficient our predictions are for describing the truth
    # this isn't just the cross-entropy of the truth with a single prediction,
    # but the sum of the cross-entropies for all the images we looked at
    cross_entropy = -tf.reduce_sum(y_*tf.log(y))

    # we ask TensorFlow to minimize cross_entropy using the gradient descent algorithm
    train_step = tf.train.GradientDescentOptimizer(0.01).minimize(cross_entropy)

    init = tf.initialize_all_variables()
    sess = tf.Session()
    sess.run(init)

    for i in range(1000):
        batch_xs, batch_ys = mnist.train.next_batch(100)
        sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})

    correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    print(sess.run(accuracy, feed_dict={x: mnist.test.images, y_: mnist.test.labels}))

def main2(argv):

    # for training a > b
    X = [[1, 5], [1, 7], [5, 0], [8, 2]] # 4 samples
    Y = [[0, 1], [0, 1], [1, 0], [1, 0]]

    # allows us to input any number of samples
    # each sample has two features
    x = tf.placeholder(tf.float32, [None, 2])

    # we are going to learn W and b
    W = tf.Variable(tf.zeros([2, 2]))

    # y is predicted probability distribution
    # this is our actual model.
    y = tf.nn.softmax(tf.matmul(x, W) + 2)

    # y' (y_) is the true distribution. (The one-hot vector we will input)
    # y_ is a placeholder to input the correct answers
    y_ = tf.placeholder(tf.float32, [None, 2])

    # cross entropy measures how inefficient our predictions are for describing the truth
    # this isn't just the cross-entropy of the truth with a single prediction,
    # but the sum of the cross-entropies for all the images we looked at
    cross_entropy = -tf.reduce_sum(y_*tf.log(y))

    # we ask TensorFlow to minimize cross_entropy using the gradient descent algorithm
    train_step = tf.train.GradientDescentOptimizer(0.01).minimize(cross_entropy)

    init = tf.initialize_all_variables()
    sess = tf.Session()
    sess.run(init)

    batch_xs, batch_ys = X, Y
    # batch_xs = np.reshape(batch_xs, (-1, 2))
    sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})


    test_X = [[3, 4], [5, 8], [5, 0], [8, 2], [6,7]] # 4 samples
    test_Y = [[0, 1], [0, 1], [1, 0], [1, 0], [0,1]]

    correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    print(sess.run(accuracy, feed_dict={x:test_X, y_: test_Y}))


if __name__ == "__main__":
    main2(sys.argv[1:])