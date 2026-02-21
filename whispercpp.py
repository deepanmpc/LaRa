import numpy as np
import sounddevice as sd
from pywhispercpp.model import Model

# Initialize the model (using small.en which you already have)
model = Model('small.en', n_threads=6)

# Audio settings
FS = 16000  # Whisper expects 16kHz
CHANNELS = 1

def callback(indata, frames, time, status):
    if status:
        print(status)
    
    # Convert audio to the format Whisper expects (float32)
    audio_data = indata.flatten().astype(np.float32)
    
    # Transcribe the chunk
    # We use a tiny segment_callback to print text immediately
    model.transcribe(audio_data, print_realtime=True)

print("\n--- M2 Metal Accelerated Streaming ---")
print("Listening... Press Ctrl+C to stop.\n")

try:
    with sd.InputStream(samplerate=FS, channels=CHANNELS, callback=callback, blocksize=FS * 2):
        while True:
            sd.sleep(1000)
except KeyboardInterrupt:
    print("\nStopping...")
except Exception as e:
    print(f"Error: {e}")
