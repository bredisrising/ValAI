import torch

# move from one corner to another in a single frame should result in this magnitude
THEORETICAL_MAX_MAGNITUDE = torch.linalg.norm(torch.tensor([1920., 1080.]))

MOUSE_MOVEMENT_NN_SCALE_DOWN = 1000
VIDEO_SCALE_DOWN = 10