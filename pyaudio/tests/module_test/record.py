"""
PyAudio Example: Low Level C Module test.

Record a few seconds of audio and save to a WAVE file.
"""

import _portaudio
import wave
import sys

chunk = 1024

FORMAT = _portaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

if sys.platform == 'darwin':
    CHANNELS = 1

print "* initializing"
_portaudio.initialize()

print "* opening"
stream = _portaudio.open(format = FORMAT,
                         channels = CHANNELS,
                         rate = RATE,
                         input = True,
                         frames_per_buffer = chunk)

print "* starting stream"
_portaudio.start_stream(stream)

print "* recording"
all = []

for i in range(0, 44100 / chunk * RECORD_SECONDS):
    data = _portaudio.read_stream(stream, chunk)
    all.append(data)
    
print "* stopping stream"
_portaudio.stop_stream(stream)

print "* closing stream"
_portaudio.close(stream)

# match all initialize() with terminate() calls
_portaudio.terminate()

# write data to WAVE file
data = ''.join(all)

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(_portaudio.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(data)
wf.close()


