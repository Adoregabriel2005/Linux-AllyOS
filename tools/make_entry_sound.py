"""Recria o sinal original de entrada AllyOS (sem gravações de terceiros)."""
import math
from pathlib import Path
import struct
import wave

root = Path(__file__).resolve().parents[1]
target = root / 'shell/assets/sounds/rose-entry.wav'
target.parent.mkdir(parents=True, exist_ok=True)
rate = 22050
notes = [(0.0, 523.251), (0.16, 659.255), (0.32, 783.991), (0.48, 1046.502)]
frames = bytearray()
for index in range(int(rate * 1.65)):
    time = index / rate
    value = 0.0
    for start, frequency in notes:
        age = time - start
        if 0 <= age < 1.1:
            envelope = min(1, age / 0.015) * math.exp(-age * 5) * min(1, (1.1-age)/0.1)
            value += envelope * (math.sin(2*math.pi*frequency*age) + 0.15*math.sin(2*math.pi*frequency*2*age))
    frames.extend(struct.pack('<h', round(max(-1, min(1, value*0.12))*32767)))
with wave.open(str(target), 'wb') as output:
    output.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
    output.writeframes(frames)
print(target, target.stat().st_size)
