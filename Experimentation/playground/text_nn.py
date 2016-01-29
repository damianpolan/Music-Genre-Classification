
import os
import sys
import numpy as np
import sknn.mlp as mlp

def main(args):
    # test AND function training
    X_train = []
    y_train = []

    X_train.append([0,0])
    y_train.append(0)

    X_train.append([0,1])
    y_train.append(0)

    X_train.append([1,0])
    y_train.append(0)

    X_train.append([1,1])
    y_train.append(1)

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    machine = mlp.Classifier(
                layers=(mlp.Layer("Sigmoid", units=4),
                        mlp.Layer("Softmax", units=2)),
                learning_rate=0.02,
                n_iter=10000)


    machine.fit(X_train, y_train)


    print str(machine.predict( np.array([[0.9, 0.9], [0, 1], [1, 0], [1, 1.5]])))
    pass



if __name__ == "__main__":
    main(sys.argv[1:])
