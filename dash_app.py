import geopandas as gpd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
from usPreLoad import persisted_geojson_ddf
from dask import compute
import plotly.express as px
from app import us_skills_ddf, us_jobs_only_with_skills_count, us_jobs_only
import requests  # Import the 'requests' module
from dask import dataframe as dd

loaded_geojson_ddf_tuple = compute(persisted_geojson_ddf)

# Access the GeoDataFrame correctly
loaded_geojson_gdf = loaded_geojson_ddf_tuple[0][0].set_geometry('geometry')

# Create Dash app
dash_app = Dash(__name__)

# Define layout including the Static Map and Scatter Map Layer
dash_app.layout = html.Div([
    html.H1("Job Postings by City"),

    # Dropdown to select DataFrame
    dcc.Dropdown(
        id='mapbox-choropleth-dropdown',
        options=[
            {'label': 'Skills by City', 'value': 'cities'},
            {'label': 'Skills by State', 'value': 'states'},
        ],
        value='cities',  # Default selection
        style={'width': '75%'},
    ),

    # Static Map
    html.Iframe(
        id='static-map',
        srcDoc=open('C:\\Users\\dakot\\Documents\\College Assignments\\Side Projects\\York Project\\static_map.html', 'r', encoding='utf-8').read(),
        style={'width': '100%', 'height': '1500px'},
    ),
])


@dash_app.callback(
    Output('static-map', 'srcDoc'),
    [Input('mapbox-choropleth-dropdown', 'value')]
)
def update_map(selected_value):
    if selected_value == 'cities':
        # Explode MultiPolygons into individual Polygons and create a new GeoDataFrame
        exploded_gdf = loaded_geojson_gdf.explode()

        # Extract latitude and longitude directly from the geometry
        exploded_gdf['lat'] = exploded_gdf.geometry.apply(lambda geom: geom.centroid.y)
        exploded_gdf['lon'] = exploded_gdf.geometry.apply(lambda geom: geom.centroid.x)

        # Add 'City' column to exploded GeoDataFrame
        exploded_gdf['City'] = exploded_gdf['NAME']

        # Merge with skills count per city data
        us_skills_and_city = dd.merge(us_skills_ddf, us_jobs_only[['job_link', 'city']], on='job_link', how='inner')
        us_jobs_only_with_skills_count = us_skills_and_city.groupby('city')['job_skills'].count().reset_index()

        # Merge with skills count per city data
        exploded_gdf = dd.merge(exploded_gdf, us_jobs_only_with_skills_count, how='left', left_on='City', right_on='city')

        # Add Scatter Map Layer for cities with data
        fig = px.scatter_mapbox(
            data_frame=exploded_gdf,  # Use the exploded GeoDataFrame with city data
            lat='lat',  # Latitude values from the new 'lat' column
            lon='lon',  # Longitude values from the new 'lon' column
            hover_name='City',  # Specify the column to display on hover
            hover_data={'job_skills': True},  # Additional data for hover
            mapbox_style='carto-positron',
            zoom=3,
            center={"lat": 37.0902, "lon": -95.7129},
        )

        # Save the figure as an HTML file
        fig.write_html('scatter_map.html')

        # Return the updated HTML content
        return open('scatter_map.html', 'r', encoding='utf-8').read()

    elif selected_value == 'states':
        # Load the scatter map HTML content for states
        return open('C:\\Users\\dakot\\Documents\\College Assignments\\Side Projects\\York Project\\scatter_map_states.html', 'r', encoding='utf-8').read()
    
# Run the app
if __name__ == '__main__':
    dash_app.run_server(debug=True)
