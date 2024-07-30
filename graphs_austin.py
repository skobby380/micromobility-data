'''
Python script to process Austin data
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
        return f'{int(x*1e-6)}M'
    elif x >= 1e3:
        return f'{int(x*1e-3)}K'
    return f'{int(x)}'

path=r'C:\Users\skobb\micromobility'
austin = pd.DataFrame()

csv_file = os.path.join(path, "new-austin-process.csv")
austin = pd.read_csv(csv_file)
austin = austin.iloc[:, 1:]
austin['startdate'] = pd.to_datetime(austin['startdate'])

sns.set_theme(rc={"figure.figsize": (25, 15)})
sns.set(font_scale= 2)
daily = austin.iloc[:,0:9].groupby(['startdate'])[['scooter']].sum()
daily = daily.reset_index()
daily['year'] = daily['startdate'].apply(lambda x: x.year) 
daily['month'] = daily['startdate'].apply(lambda x: x.month)
daily['yyyy_mm'] = pd.to_datetime(daily['startdate']).dt.strftime('%Y-%m')

daily_avg = daily.groupby(['startdate'])[['scooter']].mean().reset_index()
# sns.lineplot(data=daily_avg,x="startdate",y="scooter", errorbar = None)

# calculating the monthly and yearly totals.
monthly_total = daily.groupby(['yyyy_mm'])[['scooter']].sum().reset_index()
yearly_total = daily.groupby(['year'])[['scooter']].sum().reset_index()
yearly_total.columns = ['year', 'yearly_demand']
# rename the columns for better understanding
monthly_total['year'] = monthly_total['yyyy_mm'].str[:4].astype(int)
monthly_total = pd.merge(monthly_total, yearly_total, on='year')
# merge the dataframes together, then calculate shares
monthly_total['share'] = monthly_total['scooter'] / monthly_total['yearly_demand']
# # graph it and then turn the x labels sideways. makes for better reading
# ax = sns.lineplot(data=monthly_total,x="yyyy_mm",y="share", errorbar = None)
# ax.set(xlabel= ' ', ylabel='Share of Trips')
# ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax = 1.0, decimals = 0))
# # # ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
# ax.tick_params(axis = 'x', labelrotation = 90)
# # save the graphs
# fig = ax.get_figure()
# fig.savefig('Austinmonthlytotal-shares.png', dpi = 300)

# hourly graphs
hourly = austin.iloc[:,0:9].groupby(['startdate','starthour'])[['scooter']].sum().reset_index()
hourly['year'] = hourly['startdate'].apply(lambda x: x.year)
hourly['month'] = hourly['startdate'].apply(lambda x: x.month)
hourly['dayofweek'] = hourly['startdate'].dt.strftime('%A')
hourly_shares = hourly.groupby(['year', 'starthour'])[['scooter']].sum().reset_index()
hourly_shares = pd.merge(hourly_shares, yearly_total, on='year')
# merge the dataframes together, then calculate shares
hourly_shares['share'] = hourly_shares['scooter'] / hourly_shares['yearly_demand']
# ax = sns.lineplot(data=hourly_shares, x='starthour', y='share', hue = "year", errorbar = None)
# ax.set(xlabel='Trip Start Hour', ylabel='Share of Trips')
# ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax = 1.0, decimals = 0))
# # ax = sns.lineplot(data=hourly,x="starthour",y="scooter", hue = "year", errorbar = None)
# # ax.set(xlabel='Trip Start Hour', ylabel='Number of Rides')
# fig = ax.get_figure()
# fig.savefig('Austinhourlyavg-share.png', dpi = 300)

# heatmaps
heatmap_data = hourly.pivot_table(index='dayofweek', columns='starthour', values='scooter', aggfunc='sum')
# days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
days_order = ['Sunday', 'Saturday', 'Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday']
heatmap_data = heatmap_data.reindex(days_order)
# ax = sns.heatmap(heatmap_data, cmap = 'YlOrRd')
# ax.set(xlabel='Trip Start Hour', ylabel='Day of Week')
# cbar = ax.collections[0].colorbar
# cbar.ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
# fig = ax.get_figure()
# fig.savefig('Austinhourlyheatmap.png', dpi = 300)

# duration graphs
duration = austin.iloc[:,0:11].groupby(['startdate','starthour'])['td_median'].median().reset_index()
duration['year'] = duration['startdate'].apply(lambda x: x.year)
duration['month'] = duration['startdate'].apply(lambda x: x.month)
# ax = sns.lineplot(data=duration,x="starthour",y="td_median", errorbar = None)
# ax.set(xlabel='Trip Start Hour', ylabel='Average Trip Duration (Seconds)')
# fig = ax.get_figure()
# fig.savefig('Austindurationmedian.png', dpi = 300)

# length graphs
length = austin.iloc[:,0:13].groupby(['startdate','starthour'])['distance_mean'].median().reset_index()
length['year'] = length['startdate'].apply(lambda x: x.year)
length['month'] = length['startdate'].apply(lambda x: x.month)
# ax = sns.lineplot(data=length,x="starthour",y="distance_mean", errorbar = None)
# ax.set(xlabel='Trip Start Hour', ylabel='Average Trip Length (Miles)')
# fig = ax.get_figure()
# fig.savefig('Austinlengthmedian.png', dpi = 300)