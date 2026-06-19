#!/bin/bash
pkill -f play_noise.py 2>/dev/null
pkill -f "aplay.*Headphones" 2>/dev/null
rm -f /home/hurtig/audio/noise.pid
