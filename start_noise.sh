#!/bin/bash
nohup /home/hurtig/audio/play_noise.sh >/dev/null 2>&1 &
echo $! > /home/hurtig/audio/noise.pid
