import sounddevice as sd
import numpy as np
import wave
import io
import threading
import time
from faster_whisper import WhisperModel
from flask_socketio import SocketIO

# Constants
FREQUENCY = 16000  # Sampling rate
CHUNK_DURATION = 4  # 4s for better context
OVERLAP_DURATION = 1.5  # Reduce word loss

class SpeechTranscriber:
    def __init__(self, socketio):
        print("Loading Whisper model...")
        self.model = WhisperModel("small", device="cuda", compute_type="int8")  # No caching, loads fresh every time
        self.transcription_text = []
        self.recording_event = threading.Event()
        self.recording_thread = None
        self.socketio = socketio

    def start_recording(self):
        if not (self.recording_thread and self.recording_thread.is_alive()):
            self.recording_event.set()
            self.recording_thread = threading.Thread(target=self.record_audio, daemon=True)
            self.recording_thread.start()
            print("Recording started...")

    def stop_recording(self):
        self.recording_event.clear()
        print("Recording stopped...")
        return " ".join(self.transcription_text)

    def record_audio(self):
        print("Recording audio continuously...")
        while self.recording_event.is_set():
            start_time = time.time()

            # Record audio directly into NumPy array
            recording = sd.rec(int(CHUNK_DURATION * FREQUENCY), samplerate=FREQUENCY, channels=1, dtype='int16')
            sd.wait()

            # Convert NumPy array to in-memory WAV file
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(FREQUENCY)
                wf.writeframes(recording.tobytes())

            buffer.seek(0)  # Move to start for reading
            threading.Thread(target=self.process_transcription, args=(buffer,), daemon=True).start()

            elapsed_time = time.time() - start_time
            sleep_time = max(0, (CHUNK_DURATION - OVERLAP_DURATION) - elapsed_time)
            time.sleep(sleep_time)

    def process_transcription(self, buffer):
        transcription = self.transcribe(buffer)  # No temp file, direct from memory
        for segment in transcription:
            raw_text = segment.text.strip()
            print(raw_text)
            self.transcription_text.append(raw_text)
            print("Emitting transcription:", raw_text)
            self.socketio.emit('transcription', raw_text)

    def transcribe(self, file):
        segments, _ = self.model.transcribe(file, language="en", beam_size=3, word_timestamps=False, vad_filter=True)
        return segments
