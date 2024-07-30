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
year_segment = ['2019']
month_segment = ['1_January','2_February','3_March', 
                 '4_April','5_May','6_June','7_July','8_August', 
                 '9_September','10_October','11_November','12_December']

for i in range(len(year_segment)):
    zip_file_path = os.path.join(path, year_segment[i] + "-citibike-tripdata.zip")
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        all_files = zip_ref.namelist()

        for j in range(len(month_segment)):
            # construct the expected folder path inside the ZIP archive
            expected_folder = year_segment[i] + "-citibike-tripdata/" + month_segment[j] + "/"
            # filter the files that are in the expected folder and have a .csv extension
            csv_files = [f for f in all_files if f.startswith(expected_folder) and f.endswith('.csv')]
            
            for csv_file in csv_files:
                with zip_ref.open(csv_file) as f:
                    data = pd.read_csv(f)
                    
                    # start station
                    start = data.groupby(['start station id']).size().reset_index(name='count')
                    st1 = pd.merge(start,
                                   data[['start station id', 'start station name', 'start station latitude',
                                         'start station longitude']].drop_duplicates(subset=['start station id']), 
                                   how='left', on='start station id')
                    
                    # end station
                    end = data.groupby(['end station id']).size().reset_index(name='count')
                    en1 = pd.merge(end, 
                                   data[['end station id', 'end station name', 'end station latitude',
                                         'end station longitude']].drop_duplicates(subset=['end station id']), 
                                   how='left', on='end station id')
                    
                    # Append the results to the overall DataFrames
                    start_count = pd.concat([start_count, st1], ignore_index=True)
                    end_count = pd.concat([end_count, en1], ignore_index=True)
                    
                    print(f"Read file: {csv_file}")

# Aggregating counts for each station
start_count = start_count.groupby(['start station name', 'start station id', 'start station latitude', 'start station longitude']).sum().reset_index()
end_count = end_count.groupby(['end station name', 'end station id', 'end station latitude', 'end station longitude']).sum().reset_index()
start_count.to_csv(path_or_buf = year_segment[0] + "01-start-map-data.csv")
end_count.to_csv(path_or_buf = year_segment[0] + "01-end-map-data.csv")