'''
This script will take a full length song in wave format as input and output 10s segments of the song.
'''

import wave
import os.path



def splitSong(inputSongName, inputSongFolder, outputSongFolder):
    inputSongFileNameNoExt = os.path.splitext(inputSongName)[0]

    waveExtension = ".wav"
    inputSongFileName = inputSongFolder+'//'+inputSongName
    segmentLengthInSeconds = 10;
    try:
        waveInput = wave.open(inputSongFileName, 'rb')

        totalNumberOfFrames = waveInput.getnframes()
        frameRate = waveInput.getframerate()
        segmentLengthInFrames = (frameRate * segmentLengthInSeconds)-((frameRate * segmentLengthInSeconds)%1024)
        numberOfSegments = int(float(totalNumberOfFrames)/segmentLengthInFrames)

        #print segmentLengthInFrames

        for i in xrange(numberOfSegments):
            outputSegmentFileName = outputSongFolder+'//'+inputSongFileNameNoExt + "_part" + str(i) + waveExtension
            waveOutput = wave.open(outputSegmentFileName, 'wb')
            waveOutput.setparams(waveInput.getparams())
            frames = waveInput.readframes(segmentLengthInFrames)  # read 10s of input
            waveOutput.writeframes(frames)  # write 10 s to output segment
            waveOutput.close

        waveInput.close()
    except EOFError as e:
        print e

#splitSong("testSong.wav", "//home//christophe//IdeaProjects//GenreClassificationScripts//truncateSong//TestFolderOutput")