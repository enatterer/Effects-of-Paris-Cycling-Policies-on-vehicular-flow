import numpy as np
import pandas as pd
from sklearn.utils.random import sample_without_replacement

s = 0.0055  # km. The optimal s is found in notebook find_optimal_s.ipynb

# this class is for resampling the MFD for lane km.
class ResampledMFD():
    def __init__(self, ldd, p_sample: float, n_combinations: int):
        self.ldd = ldd
        self.p_sample = p_sample
        self.n_combinations = n_combinations

    def compute_resampled_mfd(self):
        self.resampled_mfd = ResampledMFD.resample_mfd(
            self.ldd, self.p_sample, self.n_combinations)
        resampled_mfd_envelope, capacity, critical_occupancy = ResampledMFD.get_resampled_mfd_envelope(
            self.resampled_mfd)
        self.resampled_mfd_envelope = resampled_mfd_envelope
        self.capacity = capacity
        self.critical_occupancy = critical_occupancy
        return

    def print_resampled_mfd(self):
        print(self.capacity, self.critical_occupancy)

    def resample_mfd(ldd, p_sample, n_combinations):
        n_population = ldd.iu_ac.nunique()
        n_samples = int(n_population * p_sample)
        population = ldd.iu_ac.unique().tolist()
        population_subsets = []
        seen_subsets = set()
        while len(population_subsets) < n_combinations:
            subsets_indices = tuple(
                sorted(sample_without_replacement(n_population, n_samples)))
            if subsets_indices not in seen_subsets:
                subset = [population[n] for n in subsets_indices]
                population_subsets.append(subset)
                seen_subsets.add(subsets_indices)
            else:
                continue

        subsets_mfds = []
        for idx, subset in enumerate(population_subsets):
            # print(f"Processing subset {idx+1}/{len(population_subsets)}")
            subset_ldd = ldd.loc[ldd.iu_ac.isin(subset)]
            mfd = []
            for tsp, group in subset_ldd.groupby('t_1h'):
                length_street_segments = group['geometry_detector'].length.sum()
                q_per_lane_km_total = 0
                k_per_lane_km_total = 0
                for idx, row in group.iterrows():
                    q = row['q']
                    density = row['k']/s/100
                    length = row['geometry_detector'].length
                    lanes = row['lanes_mapped']
                    q_per_lane_km = (length * q) / lanes
                    k_per_lane_km = length * density 
                    q_per_lane_km_total += q_per_lane_km
                    k_per_lane_km_total += k_per_lane_km
                
                flow = q_per_lane_km_total / length_street_segments
                density = k_per_lane_km_total / length_street_segments
                mfd.append((tsp, flow, density))
            mfd = pd.DataFrame(
                mfd, columns=['tsp', 'flow', 'density'])
            subsets_mfds.append(mfd)

        resampled_mfd = pd.concat(subsets_mfds)
        return resampled_mfd

    def get_resampled_mfd_envelope(resampled_mfd):
        num_bins = 100  # Adjust this number according to your preference
        resampled_mfd['density_bin'] = pd.cut(resampled_mfd['density'], bins=num_bins)
        # resampled_mfd['density_bin'] = pd.cut(resampled_mfd['density'],
        #                                         bins=int(resampled_mfd['density'].max()))
        # taking the median of top M flow values per occupancy bin
        resampled_mfd_envelope = []
        for bin, temp in resampled_mfd.groupby('density_bin', observed=True):
            upper_flow = temp.nlargest(100, 'flow', 'all').flow.median()
            density = bin.mid
            resampled_mfd_envelope.append((upper_flow, density))
        resampled_mfd_envelope = pd.DataFrame(
            resampled_mfd_envelope, columns=['flow', 'density'])

        # calculate 97.5th percentile of flow as the capacity
        capacity = np.percentile(
            resampled_mfd_envelope.flow, 97.5, method='nearest')
        rounded_capacity = round(capacity, 2)
        matching_rows = resampled_mfd_envelope.loc[round(
            resampled_mfd_envelope.flow, 2) == rounded_capacity]
        if not matching_rows.empty:
            critical_density = matching_rows['density'].iloc[0]
        else:
            # Handle the case where no rows match the condition
            # You might want to set a default value or raise an exception
            critical_density = None  # or any other suitable value
        return resampled_mfd_envelope, capacity, critical_density