import os
import pandas as pd
import json
from flatten_json import flatten
from multiprocessing import Pool

# Define the directory containing the state JSON files
directory = "C:\\Users\\dakot\\Documents\\College Assignments\\Side Projects\\York Project\\geojson-us-city-boundaries-master\\states"

# Function to process a single JSON file
def process_json(file_path):
    state_name = os.path.splitext(os.path.basename(file_path))[0]  # Extract state name from file name
    with open(file_path, "r") as f:
        data = json.load(f)
    flattened = flatten(data)
    flattened['State Name'] = state_name
    return flattened

if __name__ == '__main__':
    # Use multiprocessing to process JSON files in parallel
    with Pool() as pool:
        flattened_data = pool.map(process_json, [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".json")])

    # Create a DataFrame from the flattened data
    combined_data = pd.DataFrame(flattened_data)

    # Save the combined data to a CSV file
    combined_data.to_csv("combined_states_data.csv", index=False)
