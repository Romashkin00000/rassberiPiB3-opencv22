
import sounddevice as sd
import numpy as np
import soundfile as sf
from collections import deque
import threading

class AudioRecorder:
    def __init__(self, buffer_seconds, rate=44100, channels=1):
        self.rate = rate
        self.channels = channels
        self.buffer_seconds = buffer_seconds
        self.buffer = deque(maxlen=buffer_seconds * rate)
        self.recording = True
        self.lock = threading.Lock()

    def record(self):
        def callback(indata, frames, time, status):
            if status:
                print(status)
            with self.lock:
                self.buffer.extend(indata[:, 0])

        with sd.InputStream(samplerate=self.rate, channels=self.channels, callback=callback):
            while self.recording:
                sd.sleep(100)

    def save_audio(self, output_path="audio.wav"):
        with self.lock:
            data = np.array(self.buffer)
        sf.write(output_path, data, self.rate)
        return output_path

    def stop(self):
        self.recording = False