import wave

waveInput = wave.open('testSong2.wav', 'rb')
waveOutput = wave.open('testSong2cut.wav', 'wb')
time10 = 10.0
endOfSong = waveInput.getnframes();
second10 = int(time10*waveInput.getframerate())

waveInput.readframes(second10) #discard first 10s
frames = waveInput.readframes(endOfSong)

waveOutput.setparams(waveInput.getparams())
waveOutput.writeframes(frames)

waveInput.close()
waveOutput.close()