import numpy as np
import matplotlib.pyplot as plt
import pyaudiowpatch as pyaudio

RATE = 44100  # Sample rate
CHUNK = 1024  # Number of frames per buffer

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
        
print(f"Recording from: ({default_speakers['index']}){default_speakers['name']}")

stream = pyaud.open(format=pyaudio.paInt16, channels=default_speakers["maxInputChannels"], rate=int(default_speakers["defaultSampleRate"]), input=True, input_device_index=default_speakers["index"], frames_per_buffer=CHUNK)

RATE = int(default_speakers["defaultSampleRate"])
#RATE = 2048

plt.ion()  # Turn on interactive mode for real-time updating
fig, (ax_left, ax_right) = plt.subplots(2, 1, sharex=True, sharey=True)
window_buffer_left = np.zeros(int(RATE * 1), dtype=np.int16)
window_buffer_right = np.zeros(int(RATE * 1), dtype=np.int16)
x = np.arange(0, window_buffer_left.shape[0])  # Calculate time values for the x-axis

# Initialize empty buffers for the sliding windows of each channel


line_left, = ax_left.plot(x, window_buffer_left, label='Left Channel')
line_right, = ax_right.plot(x, window_buffer_right, label='Right Channel')

ax_left.legend()
ax_right.legend()

ax_left.set_title('Left Channel')
ax_right.set_title('Right Channel')

ax_left.set_ylim(-10000, 10000)  # Adjust the y-axis limits based on your data range
ax_right.set_ylim(-10000, 10000)
while True:
    # Read a chunk of stereo audio data
    stereo_data = np.frombuffer(stream.read(CHUNK * 2), dtype=np.int16)

    # Split stereo data into left and right channels
    data_left = stereo_data[::2]
    data_right = stereo_data[1::2]

    # Update the sliding window buffers for each channel
    window_buffer_left = np.roll(window_buffer_left, -CHUNK*2)
    window_buffer_left[-CHUNK*2:] = data_left

    window_buffer_right = np.roll(window_buffer_right, -CHUNK*2)
    window_buffer_right[-CHUNK*2:] = data_right

    # Update the left channel plot
    line_left.set_ydata(window_buffer_left)

    # Update the right channel plot
    line_right.set_ydata(window_buffer_right)

    fig.canvas.draw()
    fig.canvas.flush_events()

# Close the stream and PyAudio
stream.stop_stream()
stream.close()
pyaud.terminate()

# Plot the waveform
# plt.ion()  # Turn on interactive mode for real-time updating
# fig, ax = plt.subplots()
# window_buffer = np.zeros(int(RATE * 1), dtype=np.int16)
# x = np.arange(0, window_buffer.shape[0])  # Calculate time values for the x-axis

# # Initialize an empty buffer for the sliding window


# line, = ax.plot(x, window_buffer)

# ax.set_ylim(-10000, 10000)  # Adjust the y-axis limits based on your data range

# line.set_xdata(np.arange(0, window_buffer.shape[0]))

# while True:
#     # Read a chunk of audio data
#     new_data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
#     print(new_data.shape)
#     # Update the sliding window buffer
#     window_buffer = np.roll(window_buffer, -CHUNK*2)
#     window_buffer[-CHUNK*2:] = new_data

    

#     # Update the plot
#     line.set_ydata(window_buffer)
#     fig.canvas.draw()
#     fig.canvas.flush_events()

# data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)

# while True:
#     data = np.concatenate((data, np.frombuffer(stream.read(CHUNK), dtype=np.int16)))
#     print(data.shape)


#     line.set_xdata(np.arange(0, data.shape[0]))
#     ax.set_ylim(data.min(), data.max())
#     ax.set_xlim(0, data.shape[0])
#     line.set_ydata(data)
#     fig.canvas.draw()
#     fig.canvas.flush_events()

# Close the stream and PyAudio
stream.stop_stream()
stream.close()
pyaud.terminate()
