#!/bin/bash

python AudioAnalyzer.py ../TestSongs/Classical/Beethoven_Symphony_5.wav ./graphs 1000
python AudioAnalyzer.py ../TestSongs/Classical/Bizet-Carmen.wav ./graphs 1000
python AudioAnalyzer.py ../TestSongs/Classical/Mozart-Requiem.wav ./graphs 1000

python AudioAnalyzer.py ../TestSongs/Rap/50Cent-InDaClub.wav ./graphs 1000
python AudioAnalyzer.py ../TestSongs/Rap/Eminem-Stan.wav ./graphs 1000
python AudioAnalyzer.py ../TestSongs/Rap/SnoopDogg-GinandJuice.wav ./graphs 1000


