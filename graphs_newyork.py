'''
Python script to process citibike data
created on June 5, 2024, 3:26:48 PM
@author skobb
'''
import matplotlib as mpl
from matplotlib.ticker import FuncFormatter
import pandas as pd
import os
import seaborn as sns

# format the legends for any of the graphs
def thousands_formatter(x, pos):
    if x >= 1e6:
        return f'{(x*1e-6)}M'
    elif x >= 1e3:
        return f'{int(x*1e-3)}K'
    return f'{int(x)}'

# working path
path=r'C:\Users\skobb\micromobility\temporal data'
year = ['2019', '2020', '202101', '2021', '2022', '2023']
citibike = pd.DataFrame()

dataframes = []

for i in range(len(year)):
    csv_file = os.path.join(path, year[i] + "-processed-data.csv")
    data = pd.read_csv(csv_file)
    data = data.iloc[:, 1:]
    data['startdate'] = pd.to_datetime(data['startdate'])
    dataframes.append(data)
    print("attached " + year[i] + " to dataframe")

citibike = pd.concat(dataframes, ignore_index=True)
citibike.to_csv(path_or_buf = "all-processed-data.csv")

# okay
# NOW i can try and generate some graphs
sns.set_theme(rc={"figure.figsize": (25, 15)})
sns.set(font_scale= 2)
daily = citibike.iloc[:,0:3].groupby(['startdate'])[['demand']].sum()
daily = daily.reset_index()
daily['year'] = daily['startdate'].apply(lambda x: x.year) 
daily['month'] = daily['startdate'].apply(lambda x: x.month)
daily['yyyy_mm'] = pd.to_datetime(daily['startdate']).dt.strftime('%Y-%m') 

daily_avg = daily.groupby(['startdate'])[['demand']].mean().reset_index()
#sns.lineplot(data=daily_avg,x="startdate",y="demand", errorbar = None)

# calculating the monthly and yearly totals.
monthly_total = daily.groupby(['yyyy_mm'])[['demand']].sum().reset_index()
yearly_total = daily.groupby(['year'])[['demand']].sum().reset_index()
yearly_total.columns = ['year', 'yearly_demand']
# rename the columns for better understanding
monthly_total['year'] = monthly_total['yyyy_mm'].str[:4].astype(int)
monthly_total = pd.merge(monthly_total, yearly_total, on='year')
# merge the dataframes together, then calculate shares
monthly_total['share'] = monthly_total['demand'] / monthly_total['yearly_demand']
# graph it and then turn the x labels sideways. makes for better reading
# ax = sns.lineplot(data=monthly_total,x="yyyy_mm",y="share", errorbar = None)
# ax.set(xlabel=' ', ylabel='Share of Trips')
# ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax = 1.0, decimals = 0))
# # ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
# ax.tick_params(axis = 'x', labelrotation = 90)
# # save the graphs
# fig = ax.get_figure()
# fig.savefig('NYCmonthlytotal-shares.png', dpi = 300)

# sns.set_theme(rc={"figure.figsize": (20, 15)})
# calculating average hourly demand
hourly = citibike.iloc[:,0:3].groupby(['startdate','starthour'])[['demand']].sum().reset_index()
hourly['year'] = hourly['startdate'].apply(lambda x: x.year)
hourly['month'] = hourly['startdate'].apply(lambda x: x.month)
hourly['dayofweek'] = hourly['startdate'].dt.strftime('%A')
hourly_shares = hourly.groupby(['year', 'starthour'])[['demand']].sum().reset_index()
hourly_shares = pd.merge(hourly_shares, yearly_total, on='year')
# merge the dataframes together, then calculate shares
hourly_shares['share'] = hourly_shares['demand'] / hourly_shares['yearly_demand']
# ax = sns.lineplot(data=hourly_shares, x='starthour', y='share', hue = "year", errorbar = None)
# ax.set(xlabel='Trip Start Hour', ylabel='Share of Trips')
# ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax = 1.0, decimals = 0))
# # ax = sns.lineplot(data=hourly,x="starthour",y="demand", hue="year", errorbar = None)
# # ax.set(xlabel='Trip Start Hour', ylabel='Number of Rides')
# # ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
# fig = ax.get_figure()
# fig.savefig('NYChourlyavg-shares.png', dpi = 300)

# heatmaps 
heatmap_data = hourly.pivot_table(index='dayofweek', columns='starthour', values='demand', aggfunc='sum')
# days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
days_order = ['Sunday', 'Saturday', 'Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday']
heatmap_data = heatmap_data.reindex(days_order)
# ax = sns.heatmap(heatmap_data, cmap = 'YlOrRd')
# ax.set(xlabel='Trip Start Hour', ylabel='Day of Week')
# cbar = ax.collections[0].colorbar
# cbar.ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
# fig = ax.get_figure()
# fig.savefig('NYChourlyheatmap.png', dpi = 300)

# duration graphs
duration = citibike.iloc[:,0:9].groupby(['startdate','starthour'])['td_mean'].mean().reset_index()
duration['year'] = duration['startdate'].apply(lambda x: x.year)
duration['month'] = duration['startdate'].apply(lambda x: x.month)
# ax = sns.lineplot(data=duration,x="starthour",y="td_mean", errorbar = None)
# ax.set(xlabel='Trip Start Hour', ylabel='Average Trip Duration (Seconds)')
# fig = ax.get_figure()
# fig.savefig('NYCdurationmedian.png', dpi = 300)

# length graphs
length = citibike.iloc[:,0:11].groupby(['startdate','starthour'])['gcd_mean'].mean().reset_index()
length['year'] = length['startdate'].apply(lambda x: x.year)
length['month'] = length['startdate'].apply(lambda x: x.month)
# ax = sns.lineplot(data=length,x="starthour",y="gcd_mean", errorbar = None)
# ax.set(xlabel='Trip Start Hour', ylabel='Average Trip Length (Miles)')
# fig = ax.get_figure()
# fig.savefig('NYClengthmean.png', dpi = 300)