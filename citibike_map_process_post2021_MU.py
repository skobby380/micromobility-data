'''
Python script to process citibike data
created on June 5, 2024, 3:26:48 PM
@author skobb
'''

import pandas as pd
import os
import zipfile

# working path
path=r'C:\Users\skobb\micromobility\mobility_data'

start_count = pd.DataFrame()
end_count = pd.DataFrame()

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
                    print(f"Read file: {csv_file}")            

            # Calculate start station counts
            start = data.groupby(['start_station_name']).size().reset_index(name='count')
            st1 = pd.merge(start,
                           data[['start_station_id', 'start_station_name', 'start_lat',
                                 'start_lng']].drop_duplicates(subset=['start_station_name']), 
                           how='left', on='start_station_name')
            
            # Calculate end station counts
            end = data.groupby(['end_station_name']).size().reset_index(name='count')
            en1 = pd.merge(end, 
                            data[['end_station_id', 'end_station_name', 'end_lat',
                                  'end_lng']].drop_duplicates(subset=['end_station_name']), 
                            how='left', on='end_station_name')
            
            # Append the results to the overall DataFrames
            start_count = pd.concat([start_count, st1])
            end_count = pd.concat([end_count, en1])
                    
# Aggregating counts for each station
start_count_sum = start_count.groupby(['start_station_name'])['count'].sum().reset_index()
start_count_sum = pd.merge(start_count_sum, start_count[['start_station_id', 'start_station_name', 'start_lat',
      'start_lng']].drop_duplicates(subset=['start_station_name']),how='left', on='start_station_name')

end_count_sum = end_count.groupby(['end_station_name'])['count'].sum().reset_index()
end_count_sum = pd.merge(end_count_sum, end_count[['end_station_id', 'end_station_name', 'end_lat',
      'end_lng']].drop_duplicates(subset=['end_station_name']),how='left', on='end_station_name')

start_count_sum.to_csv(path_or_buf = year_segment[0] + "-start-map-data.csv")
end_count_sum.to_csv(path_or_buf = year_segment[0] + "-end-map-data.csv")
