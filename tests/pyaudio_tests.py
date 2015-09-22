import random
import struct
import time
import unittest
import wave

import pyaudio

class PyAudioTests(unittest.TestCase):
    def setUp(self):
        self.p = pyaudio.PyAudio()

    def tearDown(self):
        self.p.terminate()

    def test_system_info(self):
        """Basic system info tests"""
        self.assertTrue(self.p.get_host_api_count() > 0)
        self.assertTrue(self.p.get_device_count() > 0)
        api_info = self.p.get_host_api_info_by_index(0)
        self.assertTrue(len(api_info.items()) > 0)

    def test_input_output_blocking(self):
        """
        While playing an audio file, record its playback and compare
        with source audio file to verify audio playback and capture.

        IMPORTANT: this test requires an OS loopback sound device that
        merges output and input audio.  That is, there must a device
        that acts as both an output and input, forwarding any output
        data to the input and vice versa.  On Mac OS X, one can use
        Soundflower to create such a device.
        """
        # Create _approximately_ 1s of noise
        rate = 44100 # samples per second
        width = 2    # bytes per sample
        channels = 2
        seconds = 1

        samples_per_chunk = 1024
        total_samples = rate * seconds
        chunks = total_samples // samples_per_chunk

        audio_chunks = [
            b''.join([struct.pack('H', random.getrandbits(width * 8)) +
                      struct.pack('H', random.getrandbits(width * 8))
                     for _ in range(samples_per_chunk)])
            for __ in range(chunks)]

        input_idx, output_idx = self._find_audio_loopback()
        assert input_idx and output_idx, "No loopback device found"

        out_stream = self.p.open(
            format=self.p.get_format_from_width(width),
            channels=channels,
            rate=rate,
            output=True,
            frames_per_buffer=samples_per_chunk,
            output_device_index=output_idx)

        in_stream = self.p.open(
            format=self.p.get_format_from_width(width),
            channels=channels,
            rate=rate,
            input=True,
            frames_per_buffer=samples_per_chunk,
            input_device_index=input_idx)

        captured = []
        for chunk in audio_chunks:
            out_stream.write(chunk)
            captured.append(in_stream.read(samples_per_chunk))
        # Capture a few more frames, since there is likely some lag.
        for i in range(10):
            captured.append(in_stream.read(samples_per_chunk))

        self.assert_pcm16_nearly_equal(
            self._trim_captured(b''.join(captured)),
            b''.join(audio_chunks))

    def test_input_output_callback(self):
        """
        While playing an audio file, record its playback and compare
        with source audio file to verify audio playback and capture.
        This version uses PyAudio/PortAudio's callback approach.

        IMPORTANT: this test requires an OS loopback sound device that
        merges output and input audio.  That is, there must a device
        that acts as both an output and input, forwarding any output
        data to the input and vice versa.  On Mac OS X, one can use
        Soundflower to create such a device.
        """
        # Create _approximately_ 1s of noise
        rate = 44100 # samples per second
        width = 2    # bytes per sample
        channels = 2
        seconds = 1

        samples_per_chunk = 1024
        total_samples = rate * seconds
        chunks = total_samples // samples_per_chunk

        audio_chunks = [
            b''.join([struct.pack('H', random.getrandbits(width * 8)) +
                      struct.pack('H', random.getrandbits(width * 8))
                     for _ in range(samples_per_chunk)])
            for __ in range(chunks)]

        input_idx, output_idx = self._find_audio_loopback()
        assert input_idx and output_idx, "No loopback device found"

        state = {'count': 0}
        def out_callback(_, frame_count, time_info, status):
            if state['count'] >= len(audio_chunks):
                return ('', pyaudio.paComplete)
            rval = (audio_chunks[state['count']], pyaudio.paContinue)
            state['count'] += 1
            return rval

        captured = []
        def in_callback(in_data, frame_count, time_info, status):
            captured.append(in_data)
            return (None, pyaudio.paContinue)

        out_stream = self.p.open(
            format=self.p.get_format_from_width(width),
            channels=channels,
            rate=rate,
            output=True,
            frames_per_buffer=samples_per_chunk,
            output_device_index=output_idx,
            stream_callback=out_callback)

        in_stream = self.p.open(
            format=self.p.get_format_from_width(width),
            channels=channels,
            rate=rate,
            input=True,
            frames_per_buffer=samples_per_chunk,
            input_device_index=input_idx,
            stream_callback=in_callback)

        in_stream.start_stream()
        out_stream.start_stream()
        time.sleep(seconds + 1)
        in_stream.stop_stream()
        out_stream.stop_stream()

        self.assert_pcm16_nearly_equal(
            self._trim_captured(b''.join(captured)),
            b''.join(audio_chunks))

    def assert_pcm16_nearly_equal(self, wav1, wav2, tolerance=10):
        self.assertEquals(len(wav1), len(wav2))
        nsamples = len(wav1) / 2  # 2 bytes per sample
        wav1 = struct.unpack('%dh' % nsamples, wav1)
        wav2 = struct.unpack('%dh' % nsamples, wav2)
        max_diff = max([abs(w1 - w2) for w1, w2 in zip(wav1, wav2)])
        self.assertLessEqual(max_diff, tolerance)

    def _find_audio_loopback(self):
        """Utility to find audio loopback device."""
        input_idx, output_idx = None, None
        for device_idx in range(self.p.get_device_count()):
            devinfo = self.p.get_device_info_by_index(device_idx)
            if 'Soundflower (2ch)' in devinfo.get('name'):
                if devinfo.get('maxOutputChannels', 0) > 0:
                    output_idx = device_idx
                if devinfo.get('maxInputChannels', 0) > 0:
                    input_idx = device_idx

            if output_idx is not None and input_idx is not None:
                break

        return input_idx, output_idx

    @staticmethod
    def _trim_captured(waveform):
        """
        Utility to trim silence from beginning and end of waveform.
        """
        start_idx, end_idx = None, None
        for idx, byte in enumerate(waveform):
            if byte != b'\x00' and byte != 0:
                start_idx = idx
                break
        for idx, byte in reversed(list(enumerate(waveform))):
            if byte != b'\x00' and byte != 0:
                end_idx = idx
                break

        assert start_idx is not None
        assert end_idx is not None
        return waveform[start_idx:end_idx+1]
