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
stream = _portaudio.open(format = FORMAT, 
                         channels = CHANNELS, 
                         rate = RATE, 
                         input = True,
                         output = True,
                         frames_per_buffer = chunk)

print "* starting stream"
_portaudio.start_stream(stream)

print "* recording"

for i in range(0, 44100 / chunk * RECORD_SECONDS):
    data = _portaudio.read_stream(stream, chunk)
    _portaudio.write_stream(stream, data, chunk)
    
print "* stopping stream"
_portaudio.stop_stream(stream)

print "* closing stream"
_portaudio.close(stream)

# match all initialize() with terminate() calls
_portaudio.terminate()

