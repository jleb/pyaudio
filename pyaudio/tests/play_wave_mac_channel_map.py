""" PyAudio Example: Play a wave file """

import pyaudio
import wave
import sys

chunk = 1024

PyAudio = pyaudio.PyAudio

if len(sys.argv) < 2:
    print "Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0]
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

p = PyAudio()

s = pyaudio.paMacCoreStreamInfo(channel_map = (0, 1))

# open stream
stream = p.open(format =
                p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True,
                output_host_api_specific_stream_info = s)

# read data
data = wf.readframes(chunk)

# play stream
while data != '':
    stream.write(data)
    data = wf.readframes(chunk)

stream.stop_stream()
stream.close()

p.terminate()



