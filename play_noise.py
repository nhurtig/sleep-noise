#!/usr/bin/env python3
"""
Brown noise + 50 Hz bass (fundamental + harmonics), with time-based volume:
  21:00–21:15  linear ramp 0 → 1
  21:15–06:00  full volume
  06:00–21:00  silent
Pass --test to play at full volume regardless of time.
"""
import sys, math, random, struct, datetime

SAMPLE_RATE = 44100
BASS_FREQ   = 50.0
BASS_MIX    = 0.75
AMPLITUDE   = 0.8
CHUNK       = 4096
NOISE_SECS  = 60   # pre-generated noise buffer length

RAMP_START = 21 * 60       # 21:00
RAMP_END   = 21 * 60 + 15  # 21:15
STOP       = 6 * 60        # 06:00

test_mode = "--test" in sys.argv

def get_volume():
    if test_mode:
        return 1.0
    now = datetime.datetime.now()
    m = now.hour * 60 + now.minute + now.second / 60.0
    if RAMP_START <= m < RAMP_END:
        return (m - RAMP_START) / (RAMP_END - RAMP_START)
    elif m >= RAMP_END or m < STOP:
        return 1.0
    else:
        return 0.0

# Pre-generate normalized brown noise buffer
n = SAMPLE_RATE * NOISE_SECS
b = 0.0
noise_buf = []
for _ in range(n):
    b = (b + random.uniform(-1.0, 1.0) * 0.02) / 1.02
    noise_buf.append(b)
peak = max(abs(s) for s in noise_buf)
noise_buf = [s / peak for s in noise_buf]

max_int = int((2 ** 15 - 1) * AMPLITUDE)
w = 2 * math.pi * BASS_FREQ / SAMPLE_RATE
sample_idx = 0
noise_idx = 0
out = sys.stdout.buffer

while True:
    volume = get_volume()
    chunk = []
    for _ in range(CHUNK):
        noise_val = noise_buf[noise_idx % n]
        sine_val  = (1.00 * math.sin(w * sample_idx) +
                     0.60 * math.sin(2 * w * sample_idx) +
                     0.30 * math.sin(3 * w * sample_idx)) / 1.9
        mixed     = (1.0 - BASS_MIX) * noise_val + BASS_MIX * sine_val
        chunk.append(mixed * volume)
        sample_idx += 1
        noise_idx  += 1
    try:
        out.write(struct.pack(f"<{CHUNK}h", *(max(-32768, min(32767, int(s * max_int))) for s in chunk)))
        out.flush()
    except BrokenPipeError:
        break
