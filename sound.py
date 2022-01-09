#!/usr/bin/env python3
import pyaudio
import struct
import math


class Sounds:
    RATE = 44100
    def __init__(self):
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        p = pyaudio.PyAudio()
        self.stream = p.open(format=FORMAT, channels=CHANNELS, rate=self.RATE, output=True)
        self.presets = {}
        self.presets["hi"] = self.data_for_freq(200, 0.4)
        self.presets["bye"] = self.data_for_freq(100, 0.4)

    def data_for_freq(self, frequency: float, time: float = None):
        """get frames for a fixed frequency for a specified time or
        number of frames, if frame_count is specified, the specified
        time is ignored"""
        frame_count = int(self.RATE * time)

        remainder_frames = frame_count % self.RATE
        wavedata = []

        for i in range(frame_count):
            a = self.RATE / frequency  # number of frames per wave
            b = i / a
            # explanation for b
            # considering one wave, what part of the wave should this be
            # if we graph the sine wave in a
            # displacement vs i graph for the particle
            # where 0 is the beginning of the sine wave and
            # 1 the end of the sine wave
            # which part is "i" is denoted by b
            # for clarity you might use
            # though this is redundant since math.sin is a looping function
            # b = b - int(b)

            c = b * (2 * math.pi)
            # explanation for c
            # now we map b to between 0 and 2*math.PI
            # since 0 - 2*PI, 2*PI - 4*PI, ...
            # are the repeating domains of the sin wave (so the decimal values will
            # also be mapped accordingly,
            # and the integral values will be multiplied
            # by 2*PI and since sin(n*2*PI) is zero where n is an integer)
            d = math.sin(c) * 32767
            e = int(d)
            wavedata.append(e)

            if i < frame_count/3:
                frequency += 0.01
            if i > frame_count/3 and i < 2*frame_count/3:
                frequency -= 0.01
            if i > 2*frame_count/3:
                frequency += 0.01

        for i in range(remainder_frames):
            wavedata.append(0)

        number_of_bytes = str(len(wavedata))  
        wavedata = struct.pack(number_of_bytes + 'h', *wavedata)

        return wavedata

    def play(self, frequency: float, time: float):
        """
        play a frequency for a fixed time!
        """
        frames = self.data_for_freq(frequency, time)
        self.stream.write(frames)
        
    def play_preset(self, preset: str):
        self.stream.write(self.presets[preset])

    def cleanup(self):
        self.stream.stop_stream()
        self.stream.close()

if __name__ == "__main__":
    s=Sounds()
    s.play(200, 0.5)

