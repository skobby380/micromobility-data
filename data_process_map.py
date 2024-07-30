# -*- coding: utf-8 -*-
"""
Python script to process citibike raw data for map generation
Created on 08/28/2021
@author: 4mu
"""

import pandas as pd
import os
import geopandas as gpd

# Update working path
path=r"C:\Users\4mu\Google Drive\Bike-share_NYC\Citibike data"


#########################################################################################################
############################       Load citibike data       #############################################
#########################################################################################################
segment = ['201903','201904','201905','201906','201907','201908','201909','201910','201911','201912',
           '202001','202002','202003','202004','202005','202006','202007','202008','202009','202010',
           '202011','202012','202101','202102']

st_count = pd.DataFrame()
en_count = pd.DataFrame()

for i in range(len(segment)):
    zip_file = os.path.join(path,segment[i] + "-citibike-tripdata.csv.zip")
    data = pd.read_csv(os.path.join(path,zip_file))
    
    # Start station
    st = data.groupby(['start station name']).count()[['bikeid']].reset_index()
    st = st.rename(columns={"bikeid":"count"})
    st1 = pd.merge(st,data[['start station name','start station latitude','start station longitude']].drop_duplicates(), how='left', on='start station name')
    st1['id'] = i
    
    # End station
    en = data.groupby(['end station name']).count()[['bikeid']].reset_index()
    en = en.rename(columns={"bikeid":"count"})
    en1 = pd.merge(en, data[['end station name','end station latitude','end station longitude']].drop_duplicates(), how='left', on='end station name')
    en1['id'] = i
    
    st_count = st_count.append(st1)
    en_count = en_count.append(en1)


##############################################################################
#       Load shapefile      #############################################
##############################################################################
shapefile = gpd.read_file(os.path.join(path,"tl_2019_36_bg","NYC_bg.shp"))

st_loc_shapefile = gpd.GeoDataFrame(st_count, geometry=gpd.points_from_xy(st_count[['start station longitude']], st_count[['start station latitude']]))
st_loc_shapefile.crs = "EPSG:4269"
st_with_ct = gpd.sjoin(st_loc_shapefile, shapefile, how='inner', op='within').reset_index()
st_with_ct = st_with_ct.sort_values(by=['GEOID'])

en_loc_shapefile = gpd.GeoDataFrame(en_count, geometry=gpd.points_from_xy(en_count[['end station longitude']], en_count[['end station latitude']]))
en_loc_shapefile.crs = "EPSG:4269"
en_with_ct = gpd.sjoin(en_loc_shapefile, shapefile, how='inner', op='within').reset_index()
en_with_ct = en_with_ct.sort_values(by=['GEOID'])


# Pre-covid
pre_st = st_with_ct[st_with_ct['id']<=11]
pre_en = en_with_ct[en_with_ct['id']<=11]

pre_st_ct = pre_st.groupby(['GEOID']).sum()[['count']].reset_index()
pre_en_ct = pre_en.groupby(['GEOID']).sum()[['count']].reset_index()

# Join count with shapefile
pre_st_ct_sf = pd.merge(shapefile, pre_st_ct, how='left', on='GEOID')
pre_st_ct_sf['count'] = pre_st_ct_sf['count'].fillna(0)
pre_st_ct_sf.to_file(os.path.join(path,"map","pre_st_ct.shp"))


pre_en_ct_sf = pd.merge(shapefile, pre_en_ct, how='left', on='GEOID')
pre_en_ct_sf['count'] = pre_en_ct_sf['count'].fillna(0)
pre_en_ct_sf.to_file(os.path.join(path,"map","pre_en_ct.shp"))


# COVID
cov_st = st_with_ct[st_with_ct['id']>=12]
cov_en = en_with_ct[en_with_ct['id']>=12]

cov_st_ct = cov_st.groupby(['GEOID']).sum()[['count']].reset_index()
cov_en_ct = cov_en.groupby(['GEOID']).sum()[['count']].reset_index()


# Join count with shapefile
cov_st_ct_sf = pd.merge(shapefile, cov_st_ct, how='left', on='GEOID')
cov_st_ct_sf['count'] = cov_st_ct_sf['count'].fillna(0)
cov_st_ct_sf.to_file(os.path.join(path,"map","cov_st_ct.shp"))


cov_en_ct_sf = pd.merge(shapefile, cov_en_ct, how='left', on='GEOID')
cov_en_ct_sf['count'] = cov_en_ct_sf['count'].fillna(0)
cov_en_ct_sf.to_file(os.path.join(path,"map","cov_en_ct.shp"))

