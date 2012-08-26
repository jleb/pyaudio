""" PyAudio Example: Play a wave file (callback version) """

import pyaudio
import wave
import time
import sys

if len(sys.argv) < 2:
    print "Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0]
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

p = pyaudio.PyAudio()

def callback(frame_count, in_time, cur_time, out_time, status, in_data):
    data = wf.readframes(frame_count)
    return (data, pyaudio.paContinue)

stream = p.open(format =
                p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True,
                stream_callback = callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.close()
wf.close()

p.terminate()
