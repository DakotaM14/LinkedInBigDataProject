from flask import Flask, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import unquote
import pandas as pd
import dask
import dask.config
dask.config.set({'dataframe.query-planning-warning': False})
import dask.dataframe as dd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database2.db'
db = SQLAlchemy(app)

engine = db.create_engine("sqlite:///database2.db")

jobs_query = 'SELECT * FROM job_postings'


# Load data from SQL queries into Dask DataFrames without using a specific index column
jobs_ddf = dask.dataframe.from_pandas(pd.read_sql_query(jobs_query, engine), npartitions=2)

selected_columns = [
    'job_link', 'last_processed_time', 'got_summary', 'job_title', 'company', 'job_location',
    'search_city', 'search_country', 'job_level', 'job_type', 'job_skills'
]


# Filter jobs for valid US states
valid_us_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

us_jobs_only_ddf = jobs_ddf

# Extract state abbreviations from the job_location column
us_jobs_only_ddf['state_from_location'] = us_jobs_only_ddf['job_location'].str.split(',').str[-1].str.strip()
# Filter us_jobs_only_ddf based on valid_us_states
us_jobs_only_ddf = us_jobs_only_ddf[us_jobs_only_ddf['state_from_location'].isin(valid_us_states)]
# Drop the temporary column used for extracting state abbreviations
us_jobs_only_ddf = us_jobs_only_ddf.drop(columns=['state_from_location'])
# Convert Dask DataFrame to Pandas DataFrame
us_jobs_only_df = us_jobs_only_ddf.compute()
# Update the job_postings table in the database
us_jobs_only_df.to_sql('job_postings', engine, if_exists='replace', index=False)


@app.route('/')
def get_all_postings():
     # Use compute to convert Dask DataFrame to Pandas DataFrame
     jobs_df = us_jobs_only_df
    
     if not jobs_df.empty:
        jobs_dict = jobs_df.to_dict(orient='records')
        return jsonify(jobs_dict)
     else:
         return jsonify({'error': 'Jobs not found'})
     
@app.route('/jobs/state/<string:state>')
def get_by_state(state: str):
    state_lower = state.lower()

    us_jobs_only_ddf['state_from_location'] = us_jobs_only_ddf['job_location'].str.split(',').str[-1].str.strip()
    
    # Filter jobs by state
    state_jobs_ddf = us_jobs_only_ddf[us_jobs_only_ddf['state_from_location'].str.lower() == state_lower]

    # Check if the DataFrame has any rows
    if len(state_jobs_ddf.index) > 0:
        # Convert Dask DataFrame to Pandas DataFrame
        state_jobs_df = state_jobs_ddf.compute()

        # Extract relevant columns
        relevant_columns = state_jobs_df.columns.tolist()

        # Convert Pandas DataFrame to dictionary
        state_jobs_dict = state_jobs_df[relevant_columns].to_dict(orient='records')
        return jsonify({"state_jobs": state_jobs_dict})
    else:
        return jsonify({"state_jobs": []})

@app.route('/jobs/city/<string:job_location>')
def get_by_city(job_location: str):
    location_lower = unquote(job_location).lower()
    # Split the location string into city and state parts
    city_state_parts = location_lower.split(', ')
    
    # Extract the city part (first element) and handle cases where only city is provided
    city = city_state_parts[0] if len(city_state_parts) > 0 else None
    
    # Make the city column lowercase for case-insensitive comparison
    jobs_ddf['job_location_lower'] = jobs_ddf['job_location'].str.lower()
    
    if city:
        # Perform filtering based on both city and state (if available)
        city_jobs_ddf = jobs_ddf[
            (jobs_ddf['job_location_lower'].str.contains(city, na=False)) |
            (jobs_ddf['job_location'].str.contains(city, case=False, na=False))
        ]
    else:
        # If only city is provided, filter based on city alone
        city_jobs_ddf = jobs_ddf[jobs_ddf['job_location_lower'].str.contains(city, na=False)]

    # Convert Dask DataFrame to Pandas DataFrame
    city_jobs_df = city_jobs_ddf.compute()

    if not city_jobs_df.empty:
        city_jobs_dict = city_jobs_df.to_dict(orient='records')
        return jsonify(city_jobs_dict)
    else:
        return jsonify({'error': f'No job postings found for {city}'})
    
@app.route('/jobs/skill/<string:job_skill>')
def get_by_skill(job_skill: str):
    job_skill_lower = job_skill.lower()

    # No need to use .compute() for Pandas DataFrame
    skills_df_filtered = us_jobs_only_ddf[
        us_jobs_only_ddf['job_skills'].str.lower().str.contains(job_skill_lower, na=False)
    ]

    # Check if the DataFrame has any rows
    if len(skills_df_filtered.index) > 0:
        # Extract relevant columns
        relevant_columns = skills_df_filtered.columns.tolist()
        
        # Convert Dask DataFrame to Pandas DataFrame
        skills_df_filtered_pandas = skills_df_filtered.compute()
        
        # Convert Pandas DataFrame to dictionary
        matching_skills = skills_df_filtered_pandas[relevant_columns].to_dict(orient='records')
        return jsonify({"matching_skills": matching_skills})
    else:
        return jsonify({"matching_skills": []})
if __name__ == "__main__":
    app.run()
