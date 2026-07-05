import kagglehub
path = kagglehub.dataset_download("emmarex/plantdisease")
print("Dataset path:", path)

import os
for root, dirs, files in os.walk(path):
    if dirs:
        print("Found class folders in:", root)
        print(dirs[:5], "...")
        break