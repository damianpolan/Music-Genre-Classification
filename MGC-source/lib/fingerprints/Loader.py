



import sys
import numpy as np
from scikits.audiolab import wavread
import Feature

def main(argv):
	"""
		Loads a song and allows a set of operations to be perfomed.

		Params:
		[0] - song .wav file location
		[1] - action. Options:
								"DB" - loads song into DB (calculates metadate and all possible features as well)

		Example use: 
			python Loader.py songs/asong.wav DB

	"""

	wavPath = argv[0]
	action = argv[1]


	#load time domain data of file


	






if __name__ == "__main__":
	main(sys.argv[1:])