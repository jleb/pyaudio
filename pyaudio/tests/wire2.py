"""
PyAudio Example:

Make a wire between input and output (i.e., record a few samples
and play them back immediately).

Half Duplex version; see wire.py for Full Duplex. """

import pyaudio
import sys

chunk = 1024
WIDTH = 2 
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

if sys.platform == 'darwin':
    CHANNELS = 1

p = pyaudio.PyAudio()

# use default input device
stream_input = p.open(format =
                      p.get_format_from_width(WIDTH),
                      channels = CHANNELS,
                      rate = RATE,
                      input = True,
                      frames_per_buffer = chunk)

# use default output device
stream_output = p.open(format =
                       p.get_format_from_width(WIDTH),
                       channels = CHANNELS,
                       rate = RATE,
                       output = True,
                       frames_per_buffer = chunk)

print "* recording"
for i in range(0, 44100 / chunk * RECORD_SECONDS):
    data = stream_input.read(chunk)
    stream_output.write(data, chunk)
print "* done"

stream_input.stop_stream()
stream_output.stop_stream()
stream_input.close()
stream_output.close()
p.terminate()

