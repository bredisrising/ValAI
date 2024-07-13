import numpy as np
import matplotlib.pyplot as plt
import pyaudiowpatch as pyaudio
from scipy.signal import spectrogram
import librosa.display
import time

class SpectroCollector:
    def __init__(self):

        self.RATE = 44100  # Sample rate
        self.CHUNK = 4096  # Number of frames per buffer    

        # Initialize PyAudio
        pyaud = pyaudio.PyAudio()

        wasapi_info = pyaud.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_speakers = pyaud.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

        if not default_speakers["isLoopbackDevice"]:
            for loopback in pyaud.get_loopback_device_info_generator():
                """
                Try to find loopback device with same name(and [Loopback suffix]).
                Unfortunately, this is the most adequate way at the moment.
                """
                if default_speakers["name"] in loopback["name"]:
                    default_speakers = loopback
                    break
            else:
                exit()
        
        self.RATE = int(default_speakers["defaultSampleRate"])

        self.RATE = int(default_speakers["defaultSampleRate"])

        print(f"Recording from: ({default_speakers['index']}){default_speakers['name']}")

        self.stream = pyaud.open(format=pyaudio.paInt16, channels=default_speakers["maxInputChannels"], rate=int(default_speakers["defaultSampleRate"]), input=True, input_device_index=default_speakers["index"], frames_per_buffer=self.CHUNK)

        #RATE = int(default_speakers["defaultSampleRate"])


        self.window_buffer_left = np.zeros(int(self.RATE * 1), dtype=np.int16)
        self.window_buffer_right = np.zeros(int(self.RATE * 1), dtype=np.int16)

        # plt.ion()
        # self.fig, (self.ax_left, self.ax_right) = plt.subplots(2, 1, sharex=True, sharey=True)

    def get(self):
        stereo_data = np.frombuffer(self.stream.read(self.CHUNK), dtype=np.int16)
        

        # TODO
        # need to make it so that it outputs empty is there is not much in the buffer or something
        



        # Split stereo data into left and right channels
        data_left = stereo_data[::2]
        data_right = stereo_data[1::2]
        
        
        
        self.window_buffer_left = np.roll(self.window_buffer_left, -self.CHUNK)
        self.window_buffer_left[-self.CHUNK:] = data_left

        self.window_buffer_right = np.roll(self.window_buffer_right, -self.CHUNK)
        self.window_buffer_right[-self.CHUNK:] = data_right

        #print(window_buffer_right)

        spec_left = librosa.feature.melspectrogram(y=self.window_buffer_left.astype(np.float32), sr=self.RATE)
        spec_left_db = librosa.power_to_db(spec_left, ref=np.max)

        spec_right = librosa.feature.melspectrogram(y=self.window_buffer_right.astype(np.float32), sr=self.RATE)
        spec_right_db = librosa.power_to_db(spec_right, ref=np.max)

        spec_left_scaled = (spec_left_db - np.min(spec_left_db)) / (np.max(spec_left_db) - np.min(spec_left_db))
        spec_right_scaled = (spec_right_db - np.min(spec_right_db)) / (np.max(spec_right_db) - np.min(spec_right_db))


        # librosa.display.specshow(spec_left_scaled, x_axis='time', y_axis='mel', ax=self.ax_left, cmap="viridis")
        # librosa.display.specshow(spec_right_scaled, x_axis='time', y_axis='mel', ax=self.ax_right, cmap="viridis")

        # self.fig.canvas.draw()
        # self.fig.canvas.flush_events()

        #print(spec_left_db.shape)

        return (spec_left_scaled, spec_right_scaled)

