from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import os
import pandas as pd
import geopandas as gpd
import json

app = Dash()

# working path
spatial_data_path = r'C:\Users\skobb\micromobility\spatial data'
start_data = gpd.read_file(os.path.join(spatial_data_path,'2023-start-map-data.csv'))
start_data['count'] = pd.to_numeric(start_data['count'], errors='coerce')
start_points = gpd.GeoDataFrame(start_data,
                                    geometry=gpd.points_from_xy(start_data['start_lng'], 
                                                                start_data['start_lat']))

# Convert GeoDataFrame to Plotly Figure for NYC
def create_map(start_data):
    start_data = start_data[(start_data['start_lng'] != '') & (start_data['start_lat'] != '')]
    start_data = start_data.dropna(subset=['start_lng', 'start_lat'])
    start_points = gpd.GeoDataFrame(start_data,
                                    geometry=gpd.points_from_xy(start_data['start_lng'], 
                                                                start_data['start_lat']))
    fig = px.scatter_mapbox(start_points,
                            lat=start_points.geometry.y,
                            lon=start_points.geometry.x,
                            size=start_points['count'],
                            color=start_points['count'],  # Add this line to color by count
                            color_continuous_scale=px.colors.sequential.Plasma,  # Choose a color scale
                            size_max=15,
                            zoom=5,
                            mapbox_style="open-street-map",
                            hover_name=start_points['start_station_name'])
    fig.update_layout(
        height=500,  # Change height here
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox=dict(
            center=dict(lat=start_points.geometry.y.mean(), lon=start_points.geometry.x.mean()),
            zoom=12
        )
    )
    return fig

nyc_map = create_map(start_data)

app.layout = html.Div(children=[
    html.H1(children='Micromobility Dashboard', style={'textAlign':'center'}),

    dcc.Graph(id='city-map',style={'height': '80vh'}, figure = nyc_map)
])
if __name__ == '__main__':
    app.run(debug=True)