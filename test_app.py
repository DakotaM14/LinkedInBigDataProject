import os
import json
import geopandas as gpd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from shapely.geometry import shape
import requests

# Create Dash app
dash_app = Dash(__name__)

api_base_url = "http://localhost:5000"  # Replace with your API base URL

# Define layout including the Dropdowns and Map components
dash_app.layout = html.Div([
    html.H1("Job Postings in the U.S."),

    # Dropdown to select map type
    dcc.Dropdown(
        id='map-type-dropdown',
        options=[
            {'label': 'Jobs by State', 'value': 'state'},
            {'label': 'Jobs by City', 'value': 'city'},
        ],
        value='state',  # Default selection
        style={'width': '75%'},
    ),

    # Dropdown to select a specific state
    dcc.Dropdown(
        id='state-dropdown',
        options=[{'label': state[:-5].upper(), 'value': state[:-5].upper()} for state in os.listdir('C:\\Users\\dakot\\Documents\\College Assignments\\Side Projects\\York Project\\geojson-us-city-boundaries-master\\states') if state.endswith(".json")],
        value='',  # Default selection
        style={'width': '75%'},
    ),

    # HTML div for choropleth map
    html.Div(
        id='choropleth-map-container',
        style={'width': '100%', 'height': '800px'},
    ),
])

# Callback to update the map based on the selected type and state
@dash_app.callback(
    Output('choropleth-map-container', 'children'),
    [Input('map-type-dropdown', 'value'),
     Input('state-dropdown', 'value')],
    prevent_initial_call=True
)
def update_map(selected_type, selected_state):
    # Your logic for updating the map based on the selected type and state goes here
    # You can update the HTML content of the choropleth map container with the desired map content
    if selected_type == 'state':
        # Load GeoJSON data for the selected state from the API
        api_url = f"{api_base_url}/get_state_geojson/{selected_state}"  # Adjust the endpoint based on your API structure
        response = requests.get(api_url)

        if response.status_code == 200:
            state_geojson = response.json()
            features = state_geojson['features']
            geometry = [shape(feature['geometry']) for feature in features]
            gdf = gpd.GeoDataFrame({'geometry': geometry, 'properties': [feature['properties'] for feature in features]})

            # Create choropleth map
            fig = px.choropleth_mapbox(gdf,
                                        geojson=gdf.geometry,
                                        locations=gdf.index,
                                        color='NAME',  # Replace with your actual column
                                        mapbox_style="carto-positron",
                                        center={"lat": gdf.geometry.centroid.y.mean(),
                                                "lon": gdf.geometry.centroid.x.mean()},
                                        zoom=5,
                                        opacity=0.5,
                                        featureidkey="properties.NAME"  # Adjust to the actual key in your data
                                        )

            # Show the map
            fig.show()
            # Convert the plot to HTML
            map_content = fig.to_html()

        else:
            map_content = f"<h2>Error fetching data from API: {response.status_code}</h2>"

    else:
        # Generate HTML content for the choropleth map for other cases
        map_content = "<h2>Choropleth Map for other cases</h2>"

    return map_content

# Run the app
if __name__ == '__main__':
    dash_app.run_server(debug=True)