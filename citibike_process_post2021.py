'''
Python script to process citibike data
created on June 5, 2024, 3:26:48 PM
@author skobb
'''

import pandas as pd
import os
from geopy.distance import great_circle
import zipfile

# working path
path=r'C:\Users\skobb\micromobility\mobility_data'
citibike = pd.DataFrame()
tripno = pd.DataFrame()

# load in the citibike data
year_segment = ['2022']
month_segment = ['1_January','2_February','3_March', 
                '4_April','5_May','6_June','7_July','8_August', 
                '9_September','10_October','11_November','12_December']

# not entirely optimal, but in regards to the file reading issues
# this was the best I could find at the moment.
for i in range(len(year_segment)):
    zip_file_path = os.path.join(path, year_segment[i] + "-citibike-tripdata.zip")
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        all_files = zip_ref.namelist()

        for j in range(len(month_segment)):
            # Construct the expected folder path inside the ZIP archive
            expected_folder = year_segment[i] + "-citibike-tripdata/" + month_segment[j] + "/"
            # Filter the files that are in the expected folder and have a .csv extension
            csv_files = [f for f in all_files if f.startswith(expected_folder) and f.endswith('.csv')]
            
            data = pd.DataFrame()
            for csv_file in csv_files:
                with zip_ref.open(csv_file) as f:
                    temp_data = pd.read_csv(f)
                    data = pd.concat([data,temp_data]).reset_index(drop=True)
                    # something's wrong with these. they're not currently appending properly
                    print(f"Read file: {csv_file}")
                    # this is to assure that it's working properly

            data['startdate'] = data['started_at'].astype('datetime64[ns]').dt.date
            # this seems to format the date started
            data['starthour'] = data['started_at'].astype('datetime64[ns]').dt.hour
            # this seems to format the hour started
            data['year'] = data['started_at'].str[:4].astype('int64')

            # great circle data
            # drop rows with NaN values (this wasn't an issue in the previous set, why now ?)
            data = data.dropna(subset=['start_lat', 'start_lng', 'end_lat', 'end_lng'])
            # great_circle
            data['GCD'] = data.apply(lambda x: great_circle((x['start_lat'], x['start_lng']), 
                                    (x['end_lat'], x['end_lng'])).miles, axis=1)
            # age and gender data is absent after 2020.
            
            # bike demand
            bike_count = data.groupby(['startdate','starthour']).count()[['ride_id']]
            bike_count.columns = ['demand']
            bike_count = bike_count.reset_index()
            # type of customer
            # not absent, just worded differently
            # now divided into "member" and "casual".
            user_type = data.groupby(['startdate','starthour','member_casual']).count()[['ride_id']]
            user_type = user_type.pivot_table(index=['startdate','starthour'],columns='member_casual',
                                        values='ride_id',fill_value=0).reset_index()
            # trip duration calculations...
            # columns for tripduration are absent so i have to calculate it myself
            data['started_at'] = pd.to_datetime(data['started_at'])
            data['ended_at'] = pd.to_datetime(data['ended_at'])
            data['tripduration'] = (data['ended_at'] - data['started_at']).dt.total_seconds()
            # average trip duration
            filtered_data = data[data['tripduration'] <= 10800]
            # Calculate average trip duration
            td_mean = filtered_data.groupby(['startdate', 'starthour'])[['tripduration']].mean()
            td_mean.columns = ['td_mean']
            # median trip duration
            td_median = filtered_data.groupby(['startdate','starthour'])[['tripduration']].median()
            td_median.columns = ['td_median']
            # average great circle data.
            gcd_mean = data.groupby(['startdate','starthour'])[['GCD']].mean()
            gcd_mean.columns = ['gcd_mean']
            # median great circle data
            gcd_median =  data.groupby(['startdate','starthour'])[['GCD']].median()
            gcd_median.columns = ['gcd_median']

            merged = pd.concat([bike_count.reset_index(drop=True),
                                user_type.reset_index(drop=True),td_mean.reset_index(drop=True),
                                td_median.reset_index(drop=True),gcd_mean.reset_index(drop=True),
                                gcd_median.reset_index(drop=True)],axis=1)
            citibike = pd.concat([citibike, merged])
            citibike = citibike.reset_index(drop = True)
            # convert the data to a csv
            citibike.to_csv(path_or_buf = year_segment[i] + "-processed-data.csv")

            
print(citibike)