import pyaudio
import numpy as np
import wave

# Ajustando FRAMES_PER_BUFFER
FRAMES_PER_BUFFER = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

p = pyaudio.PyAudio()

def record_audio_from_file(file):
    wf = wave.open(file, 'rb')

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True,
        frames_per_buffer=FRAMES_PER_BUFFER
    )

    frames = []
    data = wf.readframes(FRAMES_PER_BUFFER)
    while data:
        frames.append(data)
        data = wf.readframes(FRAMES_PER_BUFFER)

    stream.write(b''.join(frames))
    stream.stop_stream()
    stream.close()
    wf.close()

    return np.frombuffer(b''.join(frames), dtype=np.int16)

def terminate():
    p.terminate()

received_data = bytearray()
file = 'test.wav'
audio_data = record_audio_from_file(file)