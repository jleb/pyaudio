"""
PyAudio Example: Low Level C Module test.

Make a wire between input and output
(i.e., record a few samples and play them back immediately).

Full Duplex version. See wire2.py for Half Duplex.
"""

import _portaudio
import sys

chunk = 1024
FORMAT = _portaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

# poor PPC macs...
if sys.platform == 'darwin':
    CHANNELS = 1

print "* initializing"
_portaudio.initialize()

print "* opening"
stream_input = _portaudio.open(format = FORMAT,
                               channels = CHANNELS,
                               rate = RATE,
                               input = True,
                               frames_per_buffer = chunk)

stream_output = _portaudio.open(format = FORMAT,
                                channels = CHANNELS,
                                rate = RATE,
                                output = True,
                                frames_per_buffer = chunk)

print "* starting stream"
_portaudio.start_stream(stream_input)
_portaudio.start_stream(stream_output)

print "* recording"

for i in range(0, 44100 / chunk * RECORD_SECONDS):
    data = _portaudio.read_stream(stream_input, chunk)
    _portaudio.write_stream(stream_output, data, chunk)
    
print "* stopping stream"
_portaudio.stop_stream(stream_input)
_portaudio.stop_stream(stream_output)

print "* closing stream"
_portaudio.close(stream_input)
_portaudio.close(stream_output)

# match initialize() with terminate() calls
_portaudio.terminate()



