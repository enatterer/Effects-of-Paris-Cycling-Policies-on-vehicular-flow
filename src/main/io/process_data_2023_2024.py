import dask_geopandas as dask_gpd
import dask.dataframe as dd
import dask
import pandas as pd

# Read the file in chunks
chunksize_bytes = 100 * 1024 * 1024  # Chunk size in bytes
gdf = dask_gpd.read_file(
    '../../data/traffic_data_2023_2024.geojson', chunksize=chunksize_bytes)
resultpath = "../../data/"
print("Compute it:")
computed = gdf.compute()
print("Drop it:")
result_filtered = computed.drop(columns = ['libelle',  'etat_trafic', 'iu_nd_amont', 'libelle_nd_amont', 'iu_nd_aval', 'libelle_nd_aval', 'etat_barre', 'date_debut', 'date_fin', 'geo_point_2d', 'geo_shape', 'geometry'], axis = 1)
print("To csv:")
result_filtered.to_csv(resultpath + "slimmed_2023_2024.csv")

# can be executed with: nohup python process_data_2023_2024.py &
