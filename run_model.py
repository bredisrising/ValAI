import torch
from recorder import capture_screenshot
from interception_controller import move_mouse
import keyboard
from model_architecture import BasicOneFrame
import dxcam
import cv2
import constants

FPS = 20
SCALE_DOWN = 5

is_run_button_pressed = False
is_running = False

nnet = BasicOneFrame()
nnet.load_state_dict(torch.load("./trained/behavior_clone.pth"))
# nnet.efficientnet.eval()
# nnet.eval()


screen_capture = dxcam.create(output_idx=0)
screen_capture.start(target_fps=FPS)

print('READY')
while True:
    if keyboard.is_pressed('ctrl + r') and not is_run_button_pressed:
        is_run_button_pressed = True
        is_running = not is_running

    elif not keyboard.is_pressed('ctrl + r'):
        is_run_button_pressed = False

    if is_running:
        frame = screen_capture.get_latest_frame()
        frame = cv2.resize(frame, (1920//5, 1080//5))
        frame = torch.tensor(frame).permute(2, 0, 1).to(torch.float32) / 255.0

        #print(frame.shape)

        with torch.no_grad():
            mouse_movements = nnet(frame.unsqueeze(0))[0]

        #print(mouse_movements.shape)

        x_move = (mouse_movements[0] * (mouse_movements[2] * constants.THEORETICAL_MAX_MAGNITUDE)).item()
        y_move = (mouse_movements[1] * (mouse_movements[2] * constants.THEORETICAL_MAX_MAGNITUDE)).item()

        x_move = int(x_move)
        y_move = int(y_move)

        print(mouse_movements)
        print(x_move, y_move)
        print()

        move_mouse(x_move, y_move)
