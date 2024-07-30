from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import os
import pandas as pd
import geopandas as gpd
import json

app = Dash()

# working path
spatial_data_path = r'C:\Users\skobb\micromobility\spatial data'
start_data = pd.read_csv(os.path.join(spatial_data_path, 'austin-starttract-data_formap.csv'))
start_data['Row Labels'] = start_data['Row Labels'].astype(str)
start_data['Sum of count'] = pd.to_numeric(start_data['Sum of count'])

# shapefile
shapefile = gpd.read_file(os.path.join(spatial_data_path, "Travis-county-Census-Tract-20240710T152036Z-001", "Travis-county-Census-Tract", "census-tract-Austin.shp"))
# merge count data to GEOID
merged_data = shapefile.merge(start_data, left_on='GEOID', right_on='Row Labels', how='left')
# convert to geoJSON
merged_geojson = json.loads(merged_data.to_json())

# function to create the map
def create_map(geojson_data):
    fig = px.choropleth_mapbox(merged_data,
                               geojson=geojson_data,
                               locations='GEOID',  # Adjust this column name if needed
                               featureidkey="properties.GEOID",
                               color='Sum of count',
                               color_continuous_scale=px.colors.sequential.YlOrRd,
                               mapbox_style="open-street-map",
                               zoom=10,
                               center={"lat": 30.2672, "lon": -97.7431},
                               opacity=0.5)
    return fig
# im the map im the map im the map im the MAAAAAAAAAP
austin = create_map(merged_geojson)

app.layout = html.Div(children=[
    html.H1(children='Micromobility Dashboard', style={'textAlign': 'center'}),

    dcc.Graph(id='city-map', style={'height': '80vh'}, figure=austin)
])

if __name__ == '__main__':
    app.run_server(debug=True)