"""
PyAudio Example: Low Level C Module test.

Play a wave file.
"""

import _portaudio
import wave
import sys

def get_format_from_width(width, unsigned = True):
    """
    Returns a PortAudio format constant for
    the specified `width`.

    :param `width`:
      The desired sample width in bytes (1, 2, 3, or 4)
    :param `unsigned`:
      For 1 byte width, specifies signed or unsigned
      format.

    :raises ValueError: for invalid `width`
    :rtype: `PaSampleFormat`

    """
    p = _portaudio

    if width == 1:
        if unsigned:
            return p.paUInt8
        else:
            return p.paInt8
    elif width == 2:
        return p.paInt16
    elif width == 3:
        return p.paInt24
    elif width == 4:
        return p.paFloat32
    else:
        raise ValueError, "Invalid width: %d" % width


chunk = 1024

if len(sys.argv) < 2:
    print "Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0]
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')



print "* initializing"
_portaudio.initialize()

print "* opening"
stream = _portaudio.open(rate = wf.getframerate(),
                         channels = wf.getnchannels(),
                         format = get_format_from_width(wf.getsampwidth()),
                         output = True)

data = wf.readframes(chunk)

print "* starting stream"
_portaudio.start_stream(stream)

print "available: %d" % _portaudio.get_stream_write_available(stream)

while data != '':
    _portaudio.write_stream(stream, data, chunk)
    data = wf.readframes(chunk)

print "* stopping stream"
_portaudio.stop_stream(stream)

print "* closing stream"
_portaudio.close(stream)

# always match an initialize() call with a terminate()
_portaudio.terminate()


