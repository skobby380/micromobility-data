from dash import Dash, html, dcc, Output, Input
import plotly.express as px
import os
import pandas as pd
import geopandas as gpd
import json

app = Dash()
server = app.server
current_dir = os.path.dirname(__file__)

# Working paths
path = os.path.join(current_dir, '..', 'temporal data')
spatial_data_path = os.path.join(current_dir, '..', 'spatial data')

# Load temporal data
year = ['2019', '2020', '202101', '2021', '2022', '2023']
dataframes = []
for y in year:
    csv_file = os.path.join(path, y + "-processed-data.csv")
    try:
        data = pd.read_csv(csv_file)
        data = data.iloc[:, 1:]
        data['startdate'] = pd.to_datetime(data['startdate'])
        dataframes.append(data)
        print(f"Attached {y} to dataframe")
    except FileNotFoundError:
        print(f"File not found: {csv_file}")
citibike = pd.concat(dataframes, ignore_index=True)

austin_csv = os.path.join(path, "new-austin-process.csv")
austin = pd.read_csv(austin_csv)
austin = austin.iloc[:, 1:]
austin['startdate'] = pd.to_datetime(austin['startdate'])


# nyc spatial data
nyc_start_data = gpd.read_file(os.path.join(spatial_data_path, '2023-start-map-data.csv'))
nyc_start_data['count'] = pd.to_numeric(nyc_start_data['count'])
nyc_start_points = gpd.GeoDataFrame(nyc_start_data, 
                                    geometry=gpd.points_from_xy(nyc_start_data['start_lng'], 
                                                                nyc_start_data['start_lat']))

# austin spatial data
austin_start_data = pd.read_csv(os.path.join(spatial_data_path, 'austin-starttract-data_formap.csv'))
austin_start_data['Row Labels'] = austin_start_data['Row Labels'].astype(str)
austin_start_data['Sum of count'] = pd.to_numeric(austin_start_data['Sum of count'])

# austin shapefile
austin_shapefile = gpd.read_file(os.path.join(spatial_data_path, 
                                              "Travis-county-Census-Tract-20240710T152036Z-001", 
                                              "Travis-county-Census-Tract", "census-tract-Austin.shp"))
merged_austin_data = austin_shapefile.merge(austin_start_data, left_on='GEOID', right_on='Row Labels', how='left')
merged_austin_geojson = json.loads(merged_austin_data.to_json())

# function to make nyc's map
def create_nyc_map(start_data):
    start_data = start_data[(start_data['start_lng'] != '') & (start_data['start_lat'] != '')]
    start_data = start_data.dropna(subset=['start_lng', 'start_lat'])
    start_points = gpd.GeoDataFrame(start_data, 
                                    geometry=gpd.points_from_xy(start_data['start_lng'], 
                                                                start_data['start_lat']))
    fig = px.scatter_mapbox(start_points, lat=start_points.geometry.y, 
                            lon=start_points.geometry.x, size=start_points['count'],
                            color=start_points['count'], 
                            color_continuous_scale=px.colors.sequential.Plasma, size_max=15, zoom=10,
                            mapbox_style="open-street-map", 
                            hover_name=start_points['start_station_name'])
    fig.update_layout(height=500, margin={"r":0,"t":0,"l":0,"b":0}, 
                      mapbox=dict(center=dict(lat=start_points.geometry.y.mean(), 
                                              lon=start_points.geometry.x.mean()), zoom=12),
                      title="Most Popular Citibike Stations (2023)")
    return fig

# function to make austin's map
def create_austin_map(geojson_data):
    fig = px.choropleth_mapbox(merged_austin_data, geojson=geojson_data, locations='GEOID', 
                               featureidkey="properties.GEOID",
                               color='Sum of count', 
                               color_continuous_scale=px.colors.sequential.YlOrRd, 
                               mapbox_style="open-street-map",
                               zoom=10, center={"lat": 30.2672, "lon": -97.7431}, opacity=0.5)
    fig.update_layout(height=500, margin={"r":0,"t":0,"l":0,"b":0},
                      title="Most Popular E-scooter Areas (2018-2022)")
    return fig

app.layout = html.Div(children=[
    html.H1(children='Micromobility Dashboard', style={'textAlign': 'center', 'fontFamily': 'Arial'}),
    html.P("This dashboard provides an interactive visualization of micromobility data, "
           "allowing you to explore trip patterns and demand for Citibikes in New York City and e-scooters in Austin. "
           "Select a city from the dropdown to view detailed graphs on trip volumes, trip duration, and more."),
    dcc.Dropdown(
        id='city-dropdown',
        options=[
            {'label': 'New York City', 'value': 'nyc'},
            {'label': 'Austin', 'value': 'austin'}
        ],
        value='nyc'
    ),
    dcc.Graph(id='monthly-trips-graph'),
    dcc.Graph(id='monthly-shares-graph'),
    dcc.Graph(id='hourly-average-trips-graph'),
    dcc.Graph(id='hourly-average-shares-graph'),
    dcc.Graph(id='average-trip-duration-graph'),
    dcc.Graph(id='average-hourly-demand-graph'),
    dcc.Graph(id='average-length-graph'),
    dcc.Graph(id='city-map', style={'height': '50vh'})
    
])

@app.callback(
    [Output('monthly-trips-graph', 'figure'),
     Output('monthly-shares-graph', 'figure'),
     Output('hourly-average-trips-graph', 'figure'),
     Output('hourly-average-shares-graph', 'figure'),
     Output('average-trip-duration-graph', 'figure'),
     Output('average-hourly-demand-graph', 'figure'),
     Output('average-length-graph', 'figure'),
     Output('city-map', 'figure')],
    [Input('city-dropdown', 'value')]
)

def update_graphs(selected_city):
    if selected_city == 'nyc':
        df = citibike
        city_map = create_nyc_map(nyc_start_data)
        length = citibike.iloc[:,0:11].groupby(['startdate','starthour'])['gcd_mean'].mean().reset_index()
        length['year'] = length['startdate'].apply(lambda x: x.year)
        length['month'] = length['startdate'].apply(lambda x: x.month)
        length_sum = length.groupby(['starthour'])['gcd_mean'].mean().reset_index()
        length_fig = px.line(length_sum,x="starthour",y="gcd_mean",
                                    labels={"starthour": "Trip Start Hour", "gcd_mean": 
                                            "Average Trip Length (Miles)"}, 
                                    title='Average Length Traveled per Trip Start Hour')
    else:
        df = austin
        city_map = create_austin_map(merged_austin_geojson)
        # length graphs
        length = austin.iloc[:,0:13].groupby(['startdate','starthour'])['distance_median'].median().reset_index()
        length['year'] = length['startdate'].apply(lambda x: x.year)
        length['month'] = length['startdate'].apply(lambda x: x.month)
        length_sum = length.groupby(['starthour'])['distance_median'].median().reset_index()
        length_fig = px.line(length_sum,x="starthour",y="distance_median",
                                    labels={"starthour": "Trip Start Hour", "distance_mean": 
                                            "Average Trip Length (Miles)"}, 
                                    title='Average Length Traveled per Trip Start Hour')
        
    daily = df.iloc[:,0:3].groupby(['startdate'])[['demand']].sum().reset_index()
    daily['year'] = daily['startdate'].apply(lambda x: x.year)
    daily['month'] = daily['startdate'].apply(lambda x: x.month)
    daily['yyyy_mm'] = pd.to_datetime(daily['startdate']).dt.strftime('%Y-%m')
    monthly_total = daily.groupby(['yyyy_mm'])[['demand']].sum().reset_index()
    yearly_total = daily.groupby(['year'])[['demand']].sum().reset_index()
    yearly_total.columns = ['year', 'yearly_demand']
    # rename the columns for better understanding
    monthly_total['year'] = monthly_total['yyyy_mm'].str[:4].astype(int)
    monthly_total = pd.merge(monthly_total, yearly_total, on='year')
    # merge the dataframes together, then calculate shares
    monthly_total['share'] = monthly_total['demand'] / monthly_total['yearly_demand']
    fig1 = px.line(monthly_total, x="yyyy_mm", y="demand", 
                   labels={"yyyy_mm": " ", "demand": "Number of Trips"}, 
                   title='Number of Trips per Month and Year')
    monthly_fig_share = px.line(monthly_total,x="yyyy_mm",y="share",
                                labels={"yyyy_mm": " ", "share": "Share of Trips"}, 
                                title='Share of Trips per Month and Year')
    monthly_fig_share.update_yaxes(tickformat=".0%")

    hourly = df.iloc[:,0:3].groupby(['startdate','starthour'])[['demand']].sum().reset_index()
    hourly['year'] = hourly['startdate'].apply(lambda x: x.year)
    hourly['month'] = hourly['startdate'].apply(lambda x: x.month)
    hourly['dayofweek'] = hourly['startdate'].dt.strftime('%A')
    hourly_shares = hourly.groupby(['year', 'starthour'])[['demand']].sum().reset_index()
    hourly_shares = pd.merge(hourly_shares, yearly_total, on='year')
    # merge the dataframes together, then calculate shares
    hourly_shares['share'] = hourly_shares['demand'] / hourly_shares['yearly_demand']
    hourly_mean = hourly.groupby(['starthour', 'year'])['demand'].mean().reset_index()
    hourly_shares_mean = hourly_shares.groupby(['starthour', 'year'])[['share']].mean().reset_index()
    heatmap_data = hourly.pivot_table(index='dayofweek', columns='starthour', values='demand', aggfunc='sum')
    days_order = ['Sunday', 'Saturday', 'Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday']
    heatmap_data = heatmap_data.reindex(days_order)
    fig2 = px.imshow(heatmap_data, 
                     labels=dict(x="Trip Start Hour", y="Day of Week", color="Demand"), 
                     x=heatmap_data.columns, y=heatmap_data.index, 
                     title='Volume of Trips by Day of Week')


    duration = df.iloc[:, 0:9].groupby(['startdate', 'starthour'])['td_mean'].mean().reset_index()
    duration['year'] = duration['startdate'].apply(lambda x: x.year)
    duration['month'] = duration['startdate'].apply(lambda x: x.month)
    duration_sum = duration.groupby(['starthour'])['td_mean'].mean().reset_index()
    fig3 = px.line(duration_sum, x="starthour", y="td_mean", 
                   labels={"starthour": "Trip Start Hour", "td_mean": "Trip Duration (Seconds)"}, 
                   title="Average Trip Duration by Trip Start Hour")
    fig4 = px.line(hourly_mean, x = "starthour", y = "demand", 
                   labels={"starthour": "Trip Start Hour", "demand": "Average Demand"}, 
                   title = "Average Demand per Trip Start Hour", color = "year")
    hourly_fig_share = px.line(hourly_shares_mean,x="starthour",y="share",
                                labels={"starthour": "Trip Start Hour", "share": "Share of Trips"}, 
                                title='Share of Trips per Trip Start Hour', color = "year")
    hourly_fig_share.update_yaxes(tickformat=".0%")
    
    return city_map, fig1, monthly_fig_share, fig2, fig4, hourly_fig_share, fig3, length_fig

if __name__ == '__main__':
    app.run(debug=True)