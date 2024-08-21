import os

for root, dirs, files in os.walk("./val_range_data/"):
    print(root, dirs, files)