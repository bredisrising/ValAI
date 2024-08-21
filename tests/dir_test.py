import os

for root, dirs, files in os.walk('./val_range_data'):
    for file in sorted(files):
        print(file)