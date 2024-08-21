import socket
import numpy as np
import cv2
import keyboard

FRAME_WIDTH = 1920//5
FRAME_HEIGHT = 1080//5
FRAME_BYTES = 3 * FRAME_WIDTH * FRAME_HEIGHT
print("FRAME BYTES: ", FRAME_BYTES)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("10.0.0.28", 8080))
sock.listen(1)

print("server is listening...")
connection, address = sock.accept()

while not keyboard.is_pressed("ctrl + c"):
    data = b''
    while len(data) < FRAME_BYTES:
        packet = connection.recv(FRAME_BYTES - len(data))
        data += packet

    image = np.frombuffer(data, dtype=np.uint8)
    image = image.reshape(FRAME_HEIGHT, FRAME_WIDTH, 3)
    #print(image.shape)

    cv2.imshow('screen capture', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
connection.close()
