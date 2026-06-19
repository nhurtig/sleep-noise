#!/bin/bash
python3 /home/hurtig/audio/play_noise.py "$@" | aplay -D plughw:CARD=Headphones,DEV=0 -f S16_LE -r 44100 -c 1 -q
