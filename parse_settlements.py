import logging
import os

import geopandas as gpd


def load(filepath, state=None):
    """
    Load GeoJSON into geopandas.DataFrame optionally masking by adm1_name shapefile.
    Note: this appears not to mask by the actual shape, but rather by a bounding box around the shape?
    """

    mask = None

    if state is not None:
        state_shapes = gpd.read_file(os.path.join("data", "GRID3_Nigeria_-_State_Boundaries.geojson"))

        logging.debug(state_shapes.columns)
        logging.debug(state_shapes.head())
        logging.debug(state_shapes.iloc[0])

        mask = state_shapes[state_shapes.statename == state]

    gdf = gpd.read_file(os.path.join("data", filepath), mask=mask)

    logging.debug(gdf.columns)
    logging.debug(gdf.head())
    logging.debug(gdf.iloc[0])

    return gdf


def calculate_centroids(gdf):
    """ Add centroid (x, y) locations from settlement extent polygons """

    # https://gis.stackexchange.com/questions/372564/userwarning-when-trying-to-get-centroid-from-a-polygon-geopandas
    centroids = gdf.to_crs('+proj=cea').centroid.to_crs(gdf.crs)

    gdf['x'] = centroids.x
    gdf['y'] = centroids.y


if __name__ == "__main__":

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    # BIG file: takes ~1 minute to load + more to parse
    filepath = "GRID3_Nigeria_Settlement_Extents_Version_01.02..geojson"
    
    # state = None
    state = "Jigawa"

    gdf = load(filepath, state=state)
    calculate_centroids(gdf)

    outfile = f"{state}_population_locations.csv" if state is not None else "population_locations.csv"
    gdf[["x", "y", "population", "adm1_name", "adm2_name", "type"]].to_csv(os.path.join("data", outfile))
