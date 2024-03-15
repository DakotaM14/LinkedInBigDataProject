import pandas as pd
from sqlalchemy import create_engine
import csv

path = 'combined_states_data.csv'
db_path = 'sqlite:///database2.db'

# Create a database engine
engine = create_engine(db_path)

try:
    # Open the CSV file
    with open(path, 'r', encoding='UTF-8') as file:
        # Create a CSV reader object
        reader = csv.DictReader(file)
        
        # Iterate over each row in the CSV file
        for row in reader:
            # Convert the row to a DataFrame with a single row
            df = pd.DataFrame([row])
            
            # Write the DataFrame to the database
            df.to_sql('states_json_data', engine, index=False, if_exists='append')
    
    print("Data successfully written to the database.")
except Exception as e:
    print(f"An error occurred: {e}")