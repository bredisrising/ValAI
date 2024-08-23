import torch
from model_architecture import BasicOneFrame
import constants
import socket
import numpy as np
import cv2
import keyboard

FPS = 20
SCALE_DOWN = 5
FRAME_WIDTH = 1920//5
FRAME_HEIGHT = 1080//5
FRAME_BYTES = 3 * FRAME_WIDTH * FRAME_HEIGHT
print("FRAME BYTES: ", FRAME_BYTES)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("10.0.0.28", 8080))
sock.listen(1)

print("server is listening...")
connection, address = sock.accept()

is_run_button_pressed = False
is_running = False

nnet = BasicOneFrame()
nnet.load_state_dict(torch.load("./trained/behavior_clone.pth"))

while not keyboard.is_pressed("ctrl + c"):
    data = b''
    while len(data) < FRAME_BYTES:
        packet = connection.recv(FRAME_BYTES - len(data))
        data += packet
    

    if is_running:

        frame = np.frombuffer(data, dtype=np.uint8)
        frame = frame.reshape(FRAME_HEIGHT, FRAME_WIDTH, 3)
        #print(image.shape)

        cv2.imshow('screen capture', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        frame = torch.from_numpy(frame).to(torch.float32) / 255.0
        frame = frame.permute(1,2,0) 

        with torch.no_grad():
            mouse_movements = nnet(frame)[0]

        x_move = (mouse_movements[0] * (mouse_movements[2] * constants.THEORETICAL_MAX_MAGNITUDE)).item()
        y_move = (mouse_movements[1] * (mouse_movements[2] * constants.THEORETICAL_MAX_MAGNITUDE)).item()

        x_move = int(x_move)
        y_move = int(y_move)

        data_to_send = bytes(np.array([x_move, y_move]))

        connection.sendall(data_to_send)


    

cv2.destroyAllWindows()
connection.close()
