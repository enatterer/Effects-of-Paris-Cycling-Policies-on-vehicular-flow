import numpy as np
import numpy.linalg as la
import pandas as pd
import geopandas as gpd
from tqdm.notebook import tqdm

import osmnx as ox
import momepy
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import alphashape
from pyproj import Proj, Geod
import ast
from shapely.ops import cascaded_union, polygonize, unary_union

def get_exterior_coords(df, start_point, end_point):
    filtered_gdf = df[(df["c_ar"] >= start_point) & (df["c_ar"] <= end_point)]

    # Check if there are any polygons matching the condition
    if not filtered_gdf.empty:
        # Apply unary_union to combine the selected polygons into a single polygon
        districts_polygon = unary_union(filtered_gdf["geometry"])
    else:
        # If no polygons match the condition, union_polygon will be None
        districts_polygon = None

    return districts_polygon.exterior.coords.xy