"""
This file creates 2016.txt and 2017.txt from data downloaded on Feb 8 2017 and May 17 2017.
These new text files contain only crimes that occur in the specified year
"""
import numpy as np

# Filenames with data
data_files = ['./raw_data/ARJISPublicCrime020817.txt',
              './raw_data/ARJISPublicCrime051717.txt']

# Load all data, including duplicates
lines = []
for f in data_files:
    with open(f, "r", encoding='cp1252') as fdata:
        lines += fdata.readlines()

# Remove duplicate data
# Some duplicate data has different whitespace, so remove all whitespace
lines_nowhite = [l.replace(" ", "").replace("\r", "") for l in lines]
_, unique_idxs = np.unique(lines_nowhite, return_index=True)
unique_crimes = np.array(lines)[np.sort(unique_idxs)]

# Separate column names from data
col_line = unique_crimes[0]
unique_crimes = unique_crimes[1:]

# Separate data for 2016 and 2017
years = [l.split('"')[4].split('/')[2][:4] for l in unique_crimes]
idx_2016 = np.where(np.array(years) == '2016')[0]
idx_2017 = np.where(np.array(years) == '2017')[0]
crime_2016 = np.insert(unique_crimes[idx_2016], 0, col_line)
crime_2017 = np.insert(unique_crimes[idx_2017], 0, col_line)

# Make sure each data point went to either 2016 or 2017
np.testing.assert_equal(len(idx_2016)+len(idx_2017), len(years))

# Save 2016 and 2017 data separately
np.savetxt('raw_data/2016_records.txt', crime_2016, fmt="%s", newline='')
np.savetxt('raw_data/2017_records.txt', crime_2017, fmt="%s", newline='')
