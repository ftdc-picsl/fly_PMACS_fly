import os
import pandas as pd
import json
import sys

directory = sys.argv[1]
print("Adding diffusion info to jsons in " + directory)
print(directory)
for dirpath, _, filenames in os.walk(directory):
    for filename in filenames:
        if filename.endswith(".bval"):
            bval_path = os.path.join(dirpath, filename)
            base_name = os.path.splitext(filename)[0]
            json_path = os.path.join(dirpath, base_name + ".json")

            num_directions = 0
            unique_shells = []

            # Examine .bval file to get number of directions and unique shells
            try:
                with open(bval_path, 'r') as f:
                    content = f.read().strip()
                    words = content.split()
                    num_directions = len(words)
                    unique_shells = sorted(set(words))
            except Exception as e:
                print(f"Error reading {bval_path}: {e}")

            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r') as jf:
                        json_data = json.load(jf)
                        dwi_info = {'number of directions': num_directions, 'unique shells': unique_shells}
                        json_data.update(dwi_info)
                    with open(json_path, 'w') as outfile:
                        print("Updating diffusion info in {}".format(json_path))
                        json.dump(json_data, outfile,indent=2,sort_keys=True)
                except Exception as e:
                    print(f"Error reading {json_path}: {e}")