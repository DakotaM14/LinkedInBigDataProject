import geopandas as gpd
from dask import delayed, compute
import dask.dataframe as dd
from dask import persist
import dask

dask.config.set(scheduler='threads')
gdf = gpd.read_file('preprocessed_us_data.geojson')

# Creates a list of delayed computations for reading the GeoJSON file
geojson_ddf = dd.from_pandas(gdf, npartitions=5)

# Computes the GeoDataFrame using Dask
persisted_geojson_ddf = persist(geojson_ddf)

# Accesses the geometries from the 'geometry' column
geometries = gdf.geometry