#!/usr/bin/env python3
import wave, struct, random, sys, math

SAMPLE_RATE = 44100
DURATION_SECS = 60
AMPLITUDE = 0.8

BASS_FREQ = 60.0  # Hz fundamental
BASS_MIX = 0.50  # fraction of final mix (0.0–1.0)

output = sys.argv[1] if len(sys.argv) > 1 else "brown_noise.wav"
n_samples = SAMPLE_RATE * DURATION_SECS
max_int = 2**15 - 1

# Brown noise via leaky integrator
b = 0.0
noise = []
for _ in range(n_samples):
    b = (b + random.uniform(-1.0, 1.0) * 0.02) / 1.02
    noise.append(b)

peak = max(abs(s) for s in noise)
noise = [s / peak for s in noise]

# Bass note: fundamental + harmonics (so it's audible through small speakers)
sine = [
    1.00 * math.sin(2 * math.pi * BASS_FREQ * 1 * i / SAMPLE_RATE)
    + 0.60 * math.sin(2 * math.pi * BASS_FREQ * 2 * i / SAMPLE_RATE)
    + 0.30 * math.sin(2 * math.pi * BASS_FREQ * 3 * i / SAMPLE_RATE)
    for i in range(n_samples)
]
peak_sine = max(abs(s) for s in sine)
sine = [s / peak_sine for s in sine]

# Mix
samples = [(1.0 - BASS_MIX) * n + BASS_MIX * s for n, s in zip(noise, sine)]

peak = max(abs(s) for s in samples)
scale = (max_int * AMPLITUDE) / peak

with wave.open(output, "w") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SAMPLE_RATE)
    chunk = 4096
    for i in range(0, n_samples, chunk):
        batch = samples[i : i + chunk]
        data = struct.pack(f"<{len(batch)}h", *(int(s * scale) for s in batch))
        f.writeframes(data)

print(
    f"Generated {output} ({DURATION_SECS}s, brown noise + {BASS_FREQ}Hz sine at {int(BASS_MIX * 100)}% mix)"
)
