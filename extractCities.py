import os
import pandas as pd
import json

df = pd.read_csv('combined_cities_data.csv')

# Add a new column "City Name" with the values from the "name" column
df.insert(0, 'City Name', df['name'])

# Save the modified DataFrame back to a CSV file
df.to_csv('combined_cities_data_modified.csv', index=False)

print("Modified CSV file saved successfully.") 