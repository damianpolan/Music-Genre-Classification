

import sys
import os
import logging
  
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from algorithms import SupportVectorCLS 
from fingerprints import database
from fingerprints import tools


def main(argv):
    tools.defaultLog()

    packsize = 512


    dbControl = database.Controller()

    dbControl.getTrainingSet(['trance', 'dubstep'], -1)



    classifier = SupportVectorCLS()

    #assign descriptors and classifications


    pass

if __name__ == "__main__":
    main(sys.argv[1:])