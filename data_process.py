# -*- coding: utf-8 -*-
"""
Python script to process citibike raw data
Created on Fri Mar 12 16:28:04 2021
@author: 4mu
"""

import pandas as pd
import os
import seaborn as sns
from geopy.distance import great_circle
from datetime import datetime
import calendar
from os import walk
import numpy as np


# Update working path
path=r"C:\Users\4mu\Google Drive\Bike-share_NYC\Citibike data"


##############################################################################
#       Load citibike data       #############################################
##############################################################################
segment = ['201903','201904','201905','201906','201907','201908','201909','201910','201911','201912',
           '202001','202002','202003','202004','202005','202006','202007','202008','202009','202010',
           '202011','202012','202101','202102']
citibike = pd.DataFrame()
tripno = pd.DataFrame()
for i in range(len(segment)):
    zip_file = os.path.join(path,segment[i] + "-citibike-tripdata.csv.zip")
    data = pd.read_csv(os.path.join(path,zip_file))
    
    data['startdate'] = data['starttime'].astype('datetime64[ns]').dt.date
    # this seems to format the date started
    data['starthour'] = data['starttime'].astype('datetime64[ns]').dt.hour
    # this seems to format the hour started
    data['year'] = data['starttime'].str[:4].astype('int64')
    # year
    # problem is starting from 2021 the format changes. i really hope there's
    # some sort of logic for that.
    
    data['age'] = data['year'] - data['birth year']
    data['age15'] = data['age'].apply(lambda x: 1 if x < 16 else 0)
    data['age24'] = data['age'].apply(lambda x: 1 if (x >= 16 and x < 25) else 0)
    data['age44'] = data['age'].apply(lambda x: 1 if (x >= 25 and x < 45) else 0)
    data['age64'] = data['age'].apply(lambda x: 1 if (x >= 45 and x < 65) else 0)
    data['age85'] = data['age'].apply(lambda x: 1 if (x >= 65 and x <= 85) else 0)
    # age data
    
    age15 = data.groupby(['startdate','starthour']).sum()[['age15']].reset_index()
    age24 = data.groupby(['startdate','starthour']).sum()[['age24']].reset_index()
    age44 = data.groupby(['startdate','starthour']).sum()[['age44']].reset_index()
    age64 = data.groupby(['startdate','starthour']).sum()[['age64']].reset_index()
    age85 = data.groupby(['startdate','starthour']).sum()[['age85']].reset_index()
    
    data['GCD'] = data.apply(lambda x: great_circle((x['start station latitude'],x['start station longitude']),
                                                    (x['end station latitude'],x['end station longitude'])).miles,axis=1)
    '''man.'''
    
    bike_count = data.groupby(['startdate','starthour']).count()[['bikeid']]
    bike_count.columns = ['demand']
    bike_count = bike_count.reset_index()
    user_type = data.groupby(['startdate','starthour','usertype']).count()[['bikeid']]
    user_type = user_type.pivot_table(index=['startdate','starthour'],columns='usertype',
                                      values='bikeid',fill_value=0).reset_index()
    gender = data.groupby(['startdate','starthour','gender']).count()[['bikeid']]
    gender = gender.pivot_table(index=['startdate','starthour'],columns='gender',
                                      values='bikeid',fill_value=0)
    gender.columns = ['unkwn','male','female']
    gender = gender.reset_index()
    
    td_mean = data[data['tripduration']<=10800].groupby(['startdate','starthour'])[['tripduration']].mean()
    td_mean.columns = ['td_mean']
    
    td_median = data[data['tripduration']<=10800].groupby(['startdate','starthour'])[['tripduration']].median()
    td_median.columns = ['td_median']
    
    gcd_mean = data.groupby(['startdate','starthour'])[['GCD']].mean()
    gcd_mean.columns = ['gcd_mean']
    
    gcd_median =  data.groupby(['startdate','starthour'])[['GCD']].median()
    gcd_median.columns = ['gcd_median']
    
    merged = pd.concat([bike_count.reset_index(drop=True),user_type.reset_index(drop=True),
                        gender.reset_index(drop=True),age15.reset_index(drop=True),
                        age24.reset_index(drop=True),age44.reset_index(drop=True),
                        age64.reset_index(drop=True),age85.reset_index(drop=True),
                        td_mean.reset_index(drop=True),td_median.reset_index(drop=True),
                        gcd_mean.reset_index(drop=True),gcd_median.reset_index(drop=True)],axis=1)

    citibike = citibike.append(merged)
    tripno = tripno.append(pd.DataFrame([(segment[i],data.shape[0])]))
    

#########################################################################################
#############   Daily and hourly count data   ###########################################
#########################################################################################
daily = citibike.iloc[:,0:3].groupby(['startdate'])[['demand']].sum()
daily= daily.reset_index()
daily['year'] = daily['startdate'].apply(lambda x: x.year)
daily['month'] = daily['startdate'].apply(lambda x: x.month)
daily['covid'] = daily.apply(lambda x: "Pre-COVID" if ((x['year'] == 2019) or (x['year'] == 2020 and x['month'] < 3)) else "COVID", axis=1)

daily_avg = daily.groupby(['year','month'])[['demand']].mean().reset_index()
daily_avg['covid'] = daily_avg.apply(lambda x: "Pre-COVID" if ((x['year'] == 2019) or (x['year'] == 2020 and x['month'] < 3)) else "COVID", axis=1)

sns.lineplot(data=daily_avg,x="month",y="demand",hue="covid")
sns.boxplot(x="month",y="demand",hue="covid",data=daily,palette="Set3")
sns.violinplot(x="month",y="demand",hue="covid",data=daily)

hourly = citibike.iloc[:,0:3].groupby(['startdate','starthour'])[['demand']].sum().reset_index()
hourly['year'] = hourly['startdate'].apply(lambda x: x.year)
hourly['month'] = hourly['startdate'].apply(lambda x: x.month)
hourly['covid'] = hourly.apply(lambda x: "Pre-COVID" if ((x['year'] == 2019) or (x['year'] == 2020 and x['month'] < 3)) else "COVID", axis=1)

hourly_avg = hourly.groupby(['starthour','covid'])[['demand']].mean().reset_index()
sns.lineplot(data=hourly_avg,x="starthour",y="demand",hue="covid")


#########################################################################################
#############   Laod processed citibike data   ##########################################
#########################################################################################
cbs = pd.read_excel(os.path.join(path,"Citibike.xlsx"))
cbs['year'] = cbs['startdate'].apply(lambda x: x.year)
cbs['day'] = cbs['startdate'].apply(lambda x: x.day)
cbs['month'] = cbs['startdate'].apply(lambda x: x.month)
cbs['dow'] = cbs['startdate'].apply(lambda x: calendar.day_name[x.weekday()])
cbs['wday'] = cbs['dow'].apply(lambda x: 1 if (x != "Saturday" and x != "Sunday") else 0)

cbs['mpeak'] = cbs['starthour'].apply(lambda x: 1 if (x >= 6 and x <=9) else 0)
cbs['midpeak'] = cbs['starthour'].apply(lambda x: 1 if (x >= 10 and x <=15) else 0)
cbs['anpeak'] = cbs['starthour'].apply(lambda x: 1 if (x >= 16 and x <=18) else 0)
cbs['night'] = cbs['starthour'].apply(lambda x: 1 if (x >= 19 or x <6) else 0)


#########################################################################################
########################   Laod weather data   ##########################################
#########################################################################################

# Update working path
path=r"C:\Users\4mu\Google Drive\Bike-share_NYC\Weather Data\NY CITY CENTRAL PARK"

file2019 = next(walk(os.path.join(path,"2019")), (None, None, []))[2]
weather = pd.DataFrame()
for i in range(len(file2019)):
    temp = pd.read_excel(os.path.join(path,"2019",file2019[i]))
    weather = weather.append(temp)

file2020 = next(walk(os.path.join(path,"2020")), (None, None, []))[2]
for i in range(len(file2020)):
    temp = pd.read_excel(os.path.join(path,"2020",file2020[i]))
    weather = weather.append(temp)

file2021 = next(walk(os.path.join(path,"2021")), (None, None, []))[2]
for i in range(len(file2021)):
    temp = pd.read_excel(os.path.join(path,"2021",file2021[i]))
    weather = weather.append(temp)

weather.columns = ['date','temp','dew','precip','humid','wind_spd','wind_dir']
weather = weather.reset_index()
weather['month'] = weather['date'].str[:2].astype('int64')
weather['day'] = weather['date'].str[3:5].astype('int64')
weather['year'] = weather['date'].str[6:11].astype('int64')
weather['hour'] = weather['date'].str[11:13].astype('int64')

#merge CBS data with weather data
merged_cbs = cbs.merge(weather,how='left',left_on=['year','month','day','starthour'],right_on=['year','month','day','hour'])
merged_cbs = merged_cbs.replace("-",np.nan)
merged_cbs['dew'].fillna(merged_cbs['dew'].mean(),inplace=True) 
merged_cbs['precip'].fillna(merged_cbs['precip'].mean(),inplace=True)
merged_cbs['wind_dir'].fillna(merged_cbs['wind_dir'].mean(),inplace=True) 


#########################################################################################
########################   Laod holiday data   ##########################################
#########################################################################################
# Update working path
path=r'C:\Users\4mu\Google Drive\Bike-share_NYC'

holiday = pd.read_excel(os.path.join(path,"NYC_Holidays.xlsx"))

#merge holiday data
final = merged_cbs.merge(holiday,how='left',left_on=['startdate'],right_on=['Date'])
final['holiday'].fillna(0,inplace=True)
final['covid'] = final.apply(lambda x: "Pre-COVID" if ((x['year'] == 2019) or (x['year'] == 2020 and x['month'] < 3)) else "COVID", axis=1)