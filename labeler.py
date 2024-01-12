import pygame
import numpy as np 
import torch
from torchvision import transforms
from PIL import Image
import pickle
import cv2


# initialize pygame

data0 = pickle.load(open("./val_range_rl_data/positive/data0.pkl", "rb"))
data1 = pickle.load(open("./val_range_rl_data/positive/data1.pkl", "rb"))
data2 = pickle.load(open("./val_range_rl_data/positive/data2.pkl", "rb"))
data3 = pickle.load(open("./val_range_rl_data/positive/data3.pkl", "rb"))
data4 = pickle.load(open("./val_range_rl_data/positive/data4.pkl", "rb"))
data5 = pickle.load(open("./val_range_rl_data/positive/data5.pkl", "rb"))
data6 = pickle.load(open("./val_range_rl_data/positive/data6.pkl", "rb"))
data7 = pickle.load(open("./val_range_rl_data/positive/data7.pkl", "rb"))
data8 = pickle.load(open("./val_range_rl_data/positive/data8.pkl", "rb"))
data9 = pickle.load(open("./val_range_rl_data/positive/data9.pkl", "rb"))


mouse_labels = pickle.load(open("./mouse_labels.pkl", "rb"))
print(len(mouse_labels))


frame_trajectories = []
mouse_trajectories = []
keyboard_trajectories = []
reward_trajectories = []
rewarder = 1.0
for trajectories in [data0, data1, data2, data3, data4, data5, data6, data7, data8, data9]:
    for traj in trajectories:
        frame_trajectory = []
        keyboard_trajectory = []
        mouse_trajectory = []
        reward_trajectory = []

        for i in range(len(traj[0])-1):
            # frame = cv2.resize(np.array(traj[0][i], dtype=np.float32)[:, :, 0]/255, (0,0), fx=0.5, fy=0.5)
            # frame = frame[:, :, 0]
            # frame = frame / 255

            mouse_data = traj[2][i+1]
            keyboard_data = traj[1][i+1]
            
            mouse_dx = 0
            mouse_dy = 0

            leftclick = 0
            space = 0
            w = 0
            a = 0
            s = 0
            d = 0
            shift = 0
            ctrl = 0

            #print(mouse_data)

            for entry in mouse_data:
                mouse_dx += entry.lLastX
                mouse_dy += entry.lLastY
                
                if entry.union.structure.usButtonFlags == 1 and leftclick == 0:
                    leftclick = 1
                elif entry.union.structure.usButtonFlags == 2 and leftclick == 0:
                    leftclick = -1

            if mouse_dx == 0 and mouse_dy == 0:
                continue
            

        # normalize
            mag = (mouse_dx**2 + mouse_dy**2)**0.5
            if mag != 0:
                mouse_dx /= mag
                mouse_dy /= mag



            frame_trajectories.append(cv2.resize(np.array(traj[0][i], dtype=np.float32), (280, 150)))
            mouse_trajectories.append([mouse_dx, mouse_dy])


    #rewarder *= -1.0


pygame.init()

running = True

screen_width = 640*2
screen_height = 480*2

screen = pygame.display.set_mode((screen_width, screen_height))


num_images = len(frame_trajectories)

current_image_index = len(mouse_labels)

clicks = 0


while running and current_image_index < num_images:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                mouse_labels.append(2)
            if event.key == pygame.K_s:
                mouse_labels.append(0)
            if event.key == pygame.K_d:
                mouse_labels.append(1)

            clicks += 2

    # open image
    #image = pygame.image.load("./images/"+str(current_image_index)+".jpg")
    #image = pygame.transform.scale(image, (screen_width, screen_height))

    #pil_image = Image.open("./images/"+str(current_image_index)+".jpg")

    #tensor_image = transform(pil_image)
    frame = frame_trajectories[current_image_index].transpose(1, 0, 2)
    #print(frame.shape)
    image = pygame.surfarray.make_surface(frame)
    image = pygame.transform.scale(image, (screen_width, screen_height))

    # draw image
    screen.blit(image, (0, 0))

    if clicks == 2:
        #data[0][current_image_index] = tensor_image[0]
        
        clicks = 0
        #print()
        current_image_index += 1
        print(current_image_index/num_images, end="\r")

    pygame.display.update()

# save data as torch tensor
# torch.save(data[0], "./input.pt")
# torch.save(data[1], "./label.pt")

pickle.dump(mouse_labels, open("./mouse_wdwlabels.pkl", "wb"))







