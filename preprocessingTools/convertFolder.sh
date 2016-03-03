#This script will convert all the files in the current working directory that end in .mp3 to .wav
#It will also remove any special characters and white spaces from file names.

for i in *.mp3; do
   ffmpeg -i "$i" "${i%%.*}.wav"
done

rename 's/[^\.a-zA-Z0-9_-]+//g' *.wav

