import sys
sys.path.append("/home/damian/Music-Genre-Classification/MGC-Source/")
sys.path.append("/home/damian/Music-Genre-Classification/MGC-Source/mgc")

import pickle
import numpy as np
from mgc.database import DatabaseService
import warnings
import os
from subprocess import Popen, PIPE

def main(argv):
    """
    :param argv:
    [0] filepath to the song to be identified
    [1] filepath to the pickled SVM

    :return: outputs the genre
    """

    SVM_filepath = "/home/damian/Music-Genre-Classification/Classifiers/SVM_Latest.pickled"

    if len(argv) > 2 or len(argv) == 0:
        print "Invalid parameters. Use example:"
        print "\tpython SVM_classify.py <.wav filepath> (optional: <filepath to pickled SVM>)"
        return
    elif len(argv) == 2:
        SVM_filepath = argv[1]

    WAV_filepath = argv[0]


    MP3_filepath = WAV_filepath + ".mp3"
    # normalize the file
    p = Popen(['ffmpeg', '-i', WAV_filepath, MP3_filepath, '-y', '-v', '0'])
    p.wait()

    try:
        p = Popen(['mp3gain', '-q', '-r', '-k', '-f', MP3_filepath], stdout=PIPE)
        p.wait()
    except:
        pass

    p = Popen(['ffmpeg', '-i', MP3_filepath, WAV_filepath, '-y', '-v', '0'])
    p.wait()

    os.remove(MP3_filepath)

    learner = pickle.load(open(SVM_filepath, "rb"))

    dbs = DatabaseService()
    evaluated_features = dbs.get_features_for_song(WAV_filepath, learner.required_features)

    result = learner.predict(np.array(evaluated_features).reshape(1, -1))

    # mapp house to electronic
    if result == 'house':
        result = "electronic"

    print result

if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        main(sys.argv[1:])
