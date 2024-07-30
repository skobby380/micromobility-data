"""
Created on Mon Jun 24 10:04:12 2024
Python script to process scooter and bike data
in Austin
@author: skobb
"""

import pandas as pd
import os

# working path
path=r'C:\Users\skobb\micromobility\mobility_data'
scooter = pd.DataFrame()

data = pd.read_csv(os.path.join(path, 'Shared_Micromobility_Vehicle_Trips_20240627.csv'))

data['startdate'] = data['Start Time (US/Central)'].astype('datetime64[ns]').dt.date
# this seems to format the date started
data['starthour'] = data['Start Time (US/Central)'].astype('datetime64[ns]').dt.hour
# this seems to format the hour started

data['Trip Distance'] = pd.to_numeric(data['Trip Distance'])
# turns out this thing doesn't play nice with commas
# so i'm removing them. without some sets of data, the resulting csv would be inaccurate
# as a result, there shouldn't be any missing information.
# as far as i'm aware the problems were with the duration and the distance
data['Trip Duration'] = pd.to_numeric(data['Trip Duration'])
# why is the trip duration a string man

data['distance'] = data['Trip Distance'] * 0.0006213712
# converts the distance (in meters) into miles. for consistency with the citibike data

# bike demand
trip_count = data.groupby(['startdate','starthour']).count()[['ID']]
trip_count.columns = ['demand']
trip_count = trip_count.reset_index()
# vehicle type
vehicle_type = data.groupby(['startdate','starthour','Vehicle Type']).count()[['ID']]
vehicle_type = vehicle_type.pivot_table(index=['startdate','starthour'],columns='Vehicle Type',
                                    values='ID',fill_value=0).reset_index()
# i do think we're looking more at scooter data here but Austin does have bikes and stuff
# Calculate average trip duration
td_mean = data.groupby(['startdate', 'starthour'])[['Trip Duration']].mean()
td_mean.columns = ['td_mean']
# median trip duration
td_median = data.groupby(['startdate','starthour'])[['Trip Duration']].median()
td_median.columns = ['td_median']
# average distance data.
distance_mean = data.groupby(['startdate','starthour'])[['distance']].mean()
distance_mean.columns = ['distance_mean']
# median distance data
distance_median =  data.groupby(['startdate','starthour'])[['distance']].median()
distance_median.columns = ['distance_median']

merged = pd.concat([trip_count.reset_index(drop=True),
                    vehicle_type.reset_index(drop=True),td_mean.reset_index(drop=True),
                    td_median.reset_index(drop=True),distance_mean.reset_index(drop=True),
                    distance_median.reset_index(drop=True)],axis=1)
scooter = pd.concat([scooter, merged])
scooter = scooter.reset_index(drop = True)
# convert the data to a csv
scooter.to_csv(path_or_buf = "austin-processed-data.csv")

print("""
Processing complete.
Check directory for generated csv file.
""")
# this is to assure that it's working properly