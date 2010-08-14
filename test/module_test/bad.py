# An example of what NOT to do:
# Don't reuse a stream object after closing it!

import _portaudio
import wave
import sys

chunk = 1024

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


if len(sys.argv) < 2:
    print "Usage: %s filename.wav" % sys.argv[0]
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

print "* initializing"
_portaudio.initialize()

print "* opening"
stream = _portaudio.open(format = get_format_from_width(wf.getsampwidth()),
                         channels = wf.getnchannels(),
                         rate = wf.getframerate(),
                         input = True,
                         output = True)

data = wf.readframes(chunk)

print "* starting stream"
_portaudio.start_stream(stream)

while data != '':
    _portaudio.write_stream(stream, data, chunk)
    data = wf.readframes(chunk)

# OK...
_portaudio.close(stream)

# Fixed -- no longer relevant. An exception will be thrown.

# -----DEPRECATED COMMENT:
# BUT! don't re-use the stream object after closing it!
# Depending on the platform, this might crash Python.
print "* CRASH ----------*"
print _portaudio.get_stream_read_available(stream)

