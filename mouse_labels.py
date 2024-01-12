import pickle
import numpy as np
import cv2
import matplotlib.pyplot as plt
import keyboard

data0 = pickle.load(open("./val_range_rl_data/positive/data0.pkl", "rb"))
data1 = pickle.load(open("./val_range_rl_data/positive/data1.pkl", "rb"))
data2 = pickle.load(open("./val_range_rl_data/positive/data2.pkl", "rb"))
data3 = pickle.load(open("./val_range_rl_data/positive/data3.pkl", "rb"))
data4 = pickle.load(open("./val_range_rl_data/positive/data4.pkl", "rb"))
data5 = pickle.load(open("./val_range_rl_data/positive/data5.pkl", "rb"))

mouse_labels = []

frame_trajectories = []
mouse_trajectories = []
keyboard_trajectories = []
reward_trajectories = []
rewarder = 1.0
for trajectories in [data0, data1, data2, data3]:
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
            
                # if entry.union.structure.usButtonFlags == 0x0100 and reward == 0:
                #     reward = 1
                
                # if entry.union.structure.usButtonFlags == 0x0040 and reward == 0:
                #     reward = -1 
            

            # for entry in keyboard_data:

            #     if entry[0] == 0x57: # W
            #         if entry[1] == 1:
            #             w = -1
            #         elif entry[1] == 0:
            #             w = 1

            #     elif entry[0] == 0x41: # A
            #         if entry[1] == 1:
            #             a = -1
            #         elif entry[1] == 0:
            #             a = 1

            #     elif entry[0] == 0x53: # S
            #         if entry[1] == 1:
            #             s = -1
            #         elif entry[1] == 0:
            #             s = 1

            #     elif entry[0] == 0x44: # D
            #         if entry[1] == 1:
            #             d = -1
            #         elif entry[1] == 0:
            #             d = 1

            #     elif entry[0] == 0x20: # Space
            #         if entry[1] == 1:
            #             space = -1
            #         elif entry[1] == 0:
            #             space = 1
                
            #     elif entry[0] == 0xA0: # Shift
            #         if entry[1] == 1:
            #             shift = -1
            #         elif entry[1] == 0:
            #             shift = 1

            #     elif entry[0] == 0x11: # Ctrl
            #         if entry[1] == 1:
            #             ctrl = -1
            #         elif entry[1] == 0:
            #             ctrl = 1
        
        

        # normalize
            mag = (mouse_dx**2 + mouse_dy**2)**0.5
            if mag != 0:
                mouse_dx /= mag
                mouse_dy /= mag

            #reward = rewarder * .993**(len(traj[0])-i-1)


            # frame_trajectory.append(cv2.resize(np.array(traj[0][i], dtype=np.float32)[:, :, 0]/255.0, (0,0), fx=0.5, fy=0.5))
            # mouse_trajectory.append([mouse_dx, mouse_dy])
            # keyboard_trajectory.append([leftclick, space, w, a, s, d, shift, ctrl])
            # reward_trajectory.append(reward)

            #trajectory.append([cv2.resize(np.array(traj[0][i], dtype=np.float32)[:, :, 0]/255, (0,0), fx=0.5, fy=0.5), [mouse_dx, mouse_dy], reward])

            frame_trajectories.append(cv2.resize(np.array(traj[0][i], dtype=np.float32), (280, 150))/255.0)
            mouse_trajectories.append([mouse_dx, mouse_dy])
            # keyboard_trajectories.append(deepcopy(np.array(keyboard_trajectory)))
            # reward_trajectories.append(deepcopy(np.array(reward_trajectory)))

    #rewarder *= -1.0


chosen = None
for i in range(len(frame_trajectories)):
    plt.imshow(frame_trajectories[i])
    plt.show(block=False)
    #print(mouse_trajectories[i])
    # print(keyboard_trajectories[i])
    # print(reward_trajectories[i])
    action = -1
    while action == -1:
        if keyboard.is_pressed('q'):
            action = 0
        elif keyboard.is_pressed('w'):
            action = 1
        elif keyboard.is_pressed('e'):
            action = 2
    plt.close()
    # if k == ord('q'): # do nothing
    #     mouse_labels.append(0)
    # elif k == ord('w'): # left
    #     mouse_labels.append(1)
    # elif k == ord('e'): # right
    #     mouse_labels.append(2)


pickle.dump(mouse_labels, open("./mouse_labels.pkl", "wb"))
