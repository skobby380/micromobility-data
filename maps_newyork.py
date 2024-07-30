import os
import geopandas as gpd
import contextily as cx

# working path
path=r'C:\Users\skobb\micromobility'

end_data = gpd.read_file(os.path.join(path,'2019-end-map-data.csv'))
start_data = gpd.read_file(os.path.join(path,'2019-start-map-data.csv'))
end_data = end_data.iloc[:, 1:]
start_data = start_data.iloc[:, 1:]

# # grabs the points needed from the data
# start_points = gpd.GeoDataFrame(start_data,
#                                     geometry=gpd.points_from_xy(start_data['start station longitude'], 
#                                                                 start_data['start station latitude']))
# end_points = gpd.GeoDataFrame(end_data,
#                                     geometry=gpd.points_from_xy(end_data['end station longitude'], 
#                                                                 end_data['end station latitude']))
# start_points['count'] = start_points['count'].astype(float)
# end_points['count'] = end_points['count'].astype(float)

# grabs the points needed from the data
start_points = gpd.GeoDataFrame(start_data,
                                    geometry=gpd.points_from_xy(start_data['start_lng'], 
                                                                start_data['start_lat']))
end_points = gpd.GeoDataFrame(end_data,
                                    geometry=gpd.points_from_xy(end_data['end_lng'], 
                                                                end_data['end_lat']))
start_points['count'] = start_points['count'].astype(float)
end_points['count'] = end_points['count'].astype(float)

# plot the start points
ax = start_points.plot(figsize=(25, 20), edgecolor="k", 
                  markersize=start_points['count']*0.0025)

# # plot the end points
# ax = end_points.plot(figsize=(25, 20), edgecolor="k", 
#                   markersize=end_points['count']*0.0025)

# add basemap 
cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, crs="EPSG:4326")
ax.set_axis_off()


