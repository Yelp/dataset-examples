import folium
map_osm = folium.Map(location=[28.4595, 77.0266])
folium.Marker([45.3288, -121.6625], popup='Mt. Hood Meadows').add_to(map_osm)
folium.Marker([45.3311, -121.7113], popup='Timberline Lodge').add_to(map_osm)
map_osm.save('osm.html')
