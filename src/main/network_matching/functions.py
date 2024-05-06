import numpy as np
import numpy.linalg as la
import pandas as pd
import geopandas as gpd
from tqdm.notebook import tqdm

import osmnx as ox
from matplotlib import pyplot as plt
import momepy
import networkx as nx
from shapely.geometry import Polygon
import alphashape
from pyproj import Proj, Geod
import ast


def prepare_scores(centroid_distances, angle_distances, alpha = 0.1, maximum_distance = 50, maximum_angle = 15 * np.pi / 180.0):
    # Prepare scoring / matching
    scores = centroid_distances + alpha * angle_distances

    # Deactivate improbable matchings
    scores[centroid_distances > maximum_distance] = np.inf
    scores[angle_distances > maximum_angle] = np.inf
    return scores

def perform_matching(scores):
    matchings = []
    matched_scores = []
    # The idea is relatively simple:
    # - Find the matching with the smallest score among those with a finite value
    # - Note down the matching, and set all matching containing the two links to Inf
    # - Continue until no scores with finite value are left
    current = np.count_nonzero(~np.isfinite(scores))
    with tqdm(total = np.prod(scores.shape) - current) as progress:
        while np.count_nonzero(np.isfinite(scores)) > 0:
        # Find best score and note down
            index = np.unravel_index(np.argmin(scores), scores.shape)
            matched_scores.append(scores[index])

        # Set both invlved links to Inf
            scores[index[0], :] = np.inf
            scores[:, index[1]] = np.inf
        
        # Manage progress plotting
            update = np.count_nonzero(~np.isfinite(scores))
        
            if update > current:
                progress.update(update - current)
                current = update

            matchings.append(index)
        
    matchings = np.array(matchings) # The matchings themselves (index detectors, index osm)
    matched_scores = np.array(matched_scores) # The scores of the matchings
    return matchings, matched_scores

def line_length_in_meters(line_string):
    # Define a UTM projection for the zone containing your coordinates
    utm_zone = 31  # Assuming you are in Paris, which falls in UTM zone 31 for example
    proj = Proj(proj='utm', zone=utm_zone, ellps='WGS84')

    # Extract coordinates from the LineString
    coordinates = list(line_string.coords)

    # Transform the coordinates to UTM projection
    utm_coordinates = [proj(lon, lat) for lon, lat in coordinates]

    # Compute the distance between consecutive points in meters
    total_length = 0
    geod = Geod(ellps='WGS84')
    for i in range(len(utm_coordinates) - 1):
        lon1, lat1 = utm_coordinates[i]
        lon2, lat2 = utm_coordinates[i + 1]
        distance_meters = geod.inv(lon1, lat1, lon2, lat2)[-1]  # Use [-1] to get distance

        # Handle case of very small distances
        if np.isnan(distance_meters):
            dx = lon2 - lon1
            dy = lat2 - lat1
            distance_meters = np.sqrt(dx**2 + dy**2)
        total_length += distance_meters

    return total_length

def is_na_list(lst):
    return lst is None or len(lst) == 0 or all(pd.isna(x) for x in lst)

def parse_and_average_lanes(lanes_str):
    if isinstance(lanes_str, list):
        if is_na_list(lanes_str):
            return np.nan
        else: 
            return sum(map(int, lanes_str)) / len(lanes_str)
    else:
        if pd.isna(lanes_str):  # Check if input is NaN
            return np.nan  # Return NaN if input is NaN
    try:
        # Attempt to parse the string as a list
        lanes_list = ast.literal_eval(lanes_str)
        if isinstance(lanes_list, list):
            # If it's a list, calculate the average of list elements
            return sum(map(int, lanes_list)) / len(lanes_list)
        else:
            # If it's a single integer, return it as is
            return int(lanes_list)
    except (SyntaxError, ValueError):
        # If parsing fails or the lanes_str is not a list, parse as single integer
        return int(lanes_str)

def approximate_number_of_lanes(df_matched):
    df_matched_with_lanes_approximated = df_matched.copy()
    average_lanes_per_highway = df_matched.groupby('highway')['lanes_mapped'].mean()
    for index, row in df_matched_with_lanes_approximated.iterrows():
        if pd.isna(row['lanes_mapped']):
            df_matched_with_lanes_approximated.at[index, 'lanes_mapped'] = average_lanes_per_highway[row['highway']]
    return df_matched_with_lanes_approximated