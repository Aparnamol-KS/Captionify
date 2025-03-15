import sounddevice as sd
import numpy as np
import wave
import io
import threading
import time
from faster_whisper import WhisperModel
from flask_socketio import SocketIO

# Constants for recording
FREQUENCY = 16000  # Sampling rate (16 kHz, suitable for speech recognition)
# CHUNK_DURATION = 4  # Each recorded chunk lasts 4 seconds
# OVERLAP_DURATION = 1.5  # Overlapping duration to avoid losing words at chunk boundaries

CHUNK_DURATION = 3  # 3s chunks
OVERLAP_DURATION = 1.0  # 1s overlap


class SpeechTranscriber:
    """
    A class that records speech, processes it using the Faster-Whisper model,
    and emits real-time transcriptions using Flask-SocketIO.
    """
    def __init__(self, socketio):
        print("Loading Whisper model...")
        
        # Initialize the Whisper speech-to-text model (small variant, running on CUDA)
        self.model = WhisperModel("small", device="cuda", compute_type="int8")

        self.transcription_text = []  # Stores transcribed text
        self.recording_event = threading.Event()  # Controls recording state
        self.recording_thread = None  # Thread for continuous recording
        self.socketio = socketio  # WebSocket instance for real-time transcription

    def start_recording(self):
        """
        Starts a separate thread to continuously record audio.
        """
        if not (self.recording_thread and self.recording_thread.is_alive()):
            self.recording_event.set()  # Set event to allow recording
            self.recording_thread = threading.Thread(target=self.record_audio, daemon=True)
            self.recording_thread.start()
            print("Recording started...")

    def stop_recording(self):
        """
        Stops the recording and returns the collected transcription.
        """
        self.recording_event.clear()  # Stop recording loop
        print("Recording stopped...")
        return " ".join(self.transcription_text)  # Return the full transcription

    def record_audio(self):
        """
        Continuously records audio in chunks and sends it for transcription.
        """
        print("Recording audio continuously...")
        while self.recording_event.is_set():  # Keep recording while event is set
            start_time = time.time()  # Mark start time for synchronization

            # Record audio into a NumPy array
            recording = sd.rec(int(CHUNK_DURATION * FREQUENCY), samplerate=FREQUENCY, channels=1, dtype='int16')
            sd.wait()  # Wait for recording to finish

            # Convert NumPy array to an in-memory WAV file (avoids temporary files)
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wf:
                wf.setnchannels(1)  # Mono audio
                wf.setsampwidth(2)  # 16-bit audio format
                wf.setframerate(FREQUENCY)
                wf.writeframes(recording.tobytes())  # Write recorded data
            
            buffer.seek(0)  # Reset buffer position to the beginning

            # Process transcription in a separate thread to prevent blocking
            threading.Thread(target=self.process_transcription, args=(buffer,), daemon=True).start()

            # Ensure recording aligns with chunk duration while avoiding gaps
            elapsed_time = time.time() - start_time
            sleep_time = max(0, (CHUNK_DURATION - OVERLAP_DURATION) - elapsed_time)
            time.sleep(sleep_time)

    def process_transcription(self, buffer):
        """
        Processes recorded audio by transcribing it and emitting results in real time.
        """
        transcription = self.transcribe(buffer)  # Convert speech to text
        
        # Iterate over transcribed segments and send results to the frontend
        for segment in transcription:
            raw_text = segment.text.strip()  # Extract the text from the segment
            print(raw_text)  # Print for debugging
            self.transcription_text.append(raw_text)  # Store transcription

            print(raw_text)
            self.socketio.emit('transcription', raw_text)  # Send transcription via WebSocket

    def transcribe(self, file):
        """
        Transcribes an audio file using the Faster-Whisper model.
        - Uses VAD (Voice Activity Detection) to improve accuracy.
        - Returns a list of transcribed segments.
        """
        segments, _ = self.model.transcribe(file, language="en", beam_size=3, word_timestamps=False, vad_filter=True)
        return segments  # Return transcribed segments
