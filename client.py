import socket
import dxcam
import cv2
import torch

FPS = 30

screen_capture = dxcam.create(output_idx=1)
screen_capture.start(target_fps=FPS)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("10.0.0.28", 8080))

while True:
    frame = screen_capture.get_latest_frame()
    frame = cv2.resize(frame, (1920//5, 1080//5))
    #frame = frame.reshape

    databytes = frame.tobytes()
    print(len(databytes))

    client_socket.sendall(databytes)

    #frame = torch.tensor(frame).permute(2, 0, 1).to(torch.float32) / 255.0



client_socket.close()


