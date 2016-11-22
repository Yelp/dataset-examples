import os
import folium
import pandas as pd

print(folium.__version__)

import numpy as np

def map_locations(lons, lats, names, stars):
    # size = 100
    # lons = np.random.randint(-100, 100, size=size)
    # lats = np.random.randint(-45, 45, size=size)
    # for index, row in df2.iterrows():
    #     # print row['latitude'], row['longitude']
    #     lons.append(row['longitude'])
    #     lats.append(row['latitude'])
    locations = list(zip(lats, lons))
    popups = ['{}, Rating = {}'.format(name, stars) for name, stars in zip(names, stars)]

    from folium.plugins import MarkerCluster

    m = folium.Map(location=[np.mean(lats), np.mean(lons)],
                      tiles='Cartodb Positron', zoom_start=1)

    m.add_child(MarkerCluster(locations=locations, popups=popups))

    m.save('1000_MarkerCluster.html')

def locations():
    df = pd.read_csv('../../yelp_dataset_challenge_academic_dataset/business.csv',  low_memory=False)
    df2 = df[['latitude', 'longitude', 'name', 'stars']]
    lons = df2.head(50).longitude.tolist()
    lats = df2.head(50).latitude.tolist()
    names = df2.head(50).name.tolist()
    stars = df2.head(50).stars.tolist()
    map_locations(lons, lats, names, stars)
    # for index, row in df2.iterrows():
    #     print row['latitude'], row['longitude']
    # print df2.head(10).to_string()
    # df

locations()
