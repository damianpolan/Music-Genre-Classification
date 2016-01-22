import sys, os
import pickle

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from fingerprints import database

def main(argv):
    """

    :param argv:
    [0] filepath to the song to be identified
    [1] filepath to the pickled SVM

    :return: outputs the genre
    """
    WAV_filepath = None
    SVM_filepath = "/home/damian/Music-Genre-Classification/Classifiers/SVM_Latest.pickled"

    if len(argv) > 2 or len(argv) == 0:
        print "Invalid paramaters. Use example:"
        print "\tpython SVM_classify.py <.wav filepath> (optional: <filepath to pickled SVM>)"
        return
    elif len(argv) == 2:
        SVM_filepath = argv[1]

    WAV_filepath = argv[0]

    machine = pickle.load(open(SVM_filepath, "rb"))





import sys

if __name__ == "__main__":
    main(sys.argv[1:])
