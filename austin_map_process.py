# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 10:20:20 2024

@author: skobb
"""

import pandas as pd
import os

# working path
path=r'C:\Users\skobb\micromobility\mobility_data'
start_count = pd.DataFrame()
end_count = pd.DataFrame()

data = pd.read_csv(os.path.join(path, 'Shared_Micromobility_Vehicle_Trips_20240627.csv'))

# Start station
start = data.groupby(['Census Tract Start']).count()[['ID']].reset_index()
start = start.rename(columns={"ID":"count"})
st1 = pd.merge(start,
    data[['Census Tract Start']].drop_duplicates(), how='left', 
    on='Census Tract Start')

# End station
end = data.groupby(['Census Tract End']).count()[['ID']].reset_index()
end = end.rename(columns={"ID":"count"})
en1 = pd.merge(end,
    data[['Census Tract End']].drop_duplicates(), how='left', 
    on='Census Tract End')

start_count = pd.concat([st1])
end_count = pd.concat([en1])
# start_count.to_csv(path_or_buf = "austin-starttract-data.csv",drop=True)
end_count.to_csv(path_or_buf = "austin-endtract-data.csv")