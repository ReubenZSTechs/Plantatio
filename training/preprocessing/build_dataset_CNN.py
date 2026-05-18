import pandas as pd
import numpy as np
import os
from tqdm import tqdm

from dotenv import load_dotenv

load_dotenv()

# """
# Structure of curated dataset
# Filepath | Class 
#
# """

rows = []

for class_name in os.listdir(os.getenv('DATA_FILEPATH')):
    class_path = os.path.join(os.getenv("DATA_FILEPATH"), class_name)

    if os.path.isdir(class_path):
        for filename in tqdm(os.listdir(class_path), desc=f"{class_name}", unit='file', dynamic_ncols=True):
            if filename.lower().endswith(('.png', '.jpg', 'jpeg')):
                filepath = os.path.join(class_path, filename)

                data = (filepath, class_name)

                rows.append(data)


dir_df = pd.DataFrame(rows)
dir_df.columns = ['filepath', 'class']

save_path = os.path.join(os.getenv("CNN_DIR_FILEPATH"), "directory_dataset.csv")

dir_df.to_csv(save_path, index=False)

print(f"Directory CSV is created")