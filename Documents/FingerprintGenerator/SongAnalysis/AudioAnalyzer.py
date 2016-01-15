"""

Crates a 

"""
import sys
from scikits.audiolab import wavread
import matplotlib.pyplot as plt
import numpy as np
import os

def generateGraph_AvT(data, outputFile, nthSample=10000, name=None):
	fig1 = plt.figure()


	if(name != None): 
		plt.title(name + ' - Amplitude vs. Time')
	else:
		plt.title('Amplitude vs. Time')

	plt.xlabel('Time (# of nth samples)')
	plt.ylabel('Amplitude')
	plt.grid(True)

	graphData = []
	indexRange = range(len(data))[0::nthSample]
	for i in indexRange:
		graphData.append(data[i])


	plt.plot(indexRange, graphData)

	if(outputFile != None):
		fig1.savefig(outputFile)
	else:
		plt.show()
	

def generateGraph_AvF(data, outputFile, name=None):
	fig = plt.figure()
	ax = fig.add_subplot(111)

	if(name != None): 
		plt.title(name + ' - Amplitude vs. Frequency')
	else:
		plt.title('Amplitude vs. Frequency')

	plt.xlabel('Frequency')
	plt.ylabel('Amplitude')
	plt.grid(True)


	newData0 = []
	newData1 = []
	for i in range(len(data)):
		newData0.append(data[i][0])
		newData1.append(data[i][1])

	ax.bar(np.arange(len(data)), newData0, 0.5, color='red', linewidth=0)
	ax.bar(np.arange(len(data)) + 0.5, newData0, 0.5, color='black', linewidth=0)


	if(outputFile != None):
		fig.savefig(outputFile)
	else:
		plt.show()
	

def intoFrequencyDomain(data):
		return np.fft.fft(data)
		

def main(argv):
	"""
	arg1: song file path (.wav)
	arg2: outputFolder
	arg3: sampleLength
	"""
	#testFilePath = "/home/damian/Music-Genre-Classification/FingerprintGenerator/TestSongs/Call_Makeup_Feat_Villa-2.wav"
	
	songFilePath = argv[0]
	outputFolder = argv[1]
	sampleLength = int(argv[2])


	ampData, fs, enc = wavread(songFilePath)
	print len(ampData)
	newAmpData = []
	for el in ampData:
		newAmpData.append(el[0])
	# print fs #sampling rate
	# print enc #encoding

	freqData = intoFrequencyDomain(newAmpData[len(newAmpData) / 2:len(newAmpData) / 2 + sampleLength])

	print freqData
	return
	songname = os.path.basename(songFilePath).replace(".wav", "");

	generateGraph_AvT(ampData, outputFolder + "/" + songname + "__AvT.png", name=songname)
	generateGraph_AvF(freqData, outputFolder + "/" + songname + "__AvF.png", name=songname)

	#generate raw csv
	targetFile = open(outputFolder + "/" + songname + "__AvT.csv", 'w')
	targetFile.truncate()
	for i in range(len(ampData))[0::10000]:
		targetFile.write(str(ampData[i][0]) + "," + str(ampData[i][1]) + "\n")
	targetFile.close()



if __name__ == "__main__":
	main(sys.argv[1:])
