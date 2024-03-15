import geopandas as gpd
import plotly.express as px
from dash import dcc, html
import plotly.io as pio

def load_and_initialize_map():
    loaded_geojson_gdf = gpd.read_file('preprocessed_us_data.geojson')
    loaded_geojson_gdf = loaded_geojson_gdf.set_geometry('geometry')

    # Initialize static map
    static_map_fig = px.choropleth_mapbox(
        data_frame=loaded_geojson_gdf,
        geojson=loaded_geojson_gdf.geometry,
        locations=None,
        mapbox_style='carto-positron',
        zoom=3,
        center={"lat": 37.0902, "lon": -95.7129},
    )

    # Save the figure as an HTML file
    pio.write_html(static_map_fig, 'static_map.html')

    return static_map_fig

load_and_initialize_map()
