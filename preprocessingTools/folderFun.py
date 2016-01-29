#Goes through a folder and splits all the .wav files

import os
import sys
import splitSong
inputFolderPath = "//home//christophe//IdeaProjects//GenreClassificationScripts//truncateSong//TestFolderInput"
outputFolderPath = "//home//christophe//IdeaProjects//GenreClassificationScripts//truncateSong//TestFolderOutput"


def splitAllSongsInFolder(inputFolderPath, outputFolderPath):
    for songFile in os.listdir(inputFolderPath):
        if songFile.endswith(".wav"):
            splitSong.splitSong(songFile, outputFolderPath)

if __name__ == '__main__':
    print sys.argv
    splitAllSongsInFolder(sys.argv[1], sys.argv[2])
