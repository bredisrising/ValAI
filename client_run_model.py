import socket
import dxcam
import cv2
from interception_controller import move_mouse
import constants
import numpy as np
import keyboard

FPS = 20

screen_capture = dxcam.create(output_idx=1)
screen_capture.start(target_fps=FPS)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("10.0.0.28", 8080))

while not keyboard.is_pressed("ctrl + c"):
    frame = screen_capture.get_latest_frame()
    frame = cv2.resize(frame, (1920//5, 1080//5))
    #frame = frame.reshape

    send_data_bytes = frame.tobytes()
    # print(len(databytes))

    client_socket.sendall(send_data_bytes)

    
    receive_data_bytes = b''
    while len(receive_data_bytes) < 8:
        receive_data_bytes += client_socket.recv(8 - len(receive_data_bytes))

    recieved_mouse_movement = np.frombuffer(receive_data_bytes, dtype=np.int8)

    move_mouse(recieved_mouse_movement[0], recieved_mouse_movement[1])    



client_socket.close()


