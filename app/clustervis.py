import gzip
import json
import plotly
import plotly.graph_objects as go

import geopandas as gp
import pandas as pd
import numpy as np


################################################################################
# Load reference data as module-level globals.
#
# CLUSTER_DF = pandas dataframe consisting of clustering/ranking results
# GPDF = geopandas dataframe with all of the census tract geometries
#
# This module should be loaded in the background since this may take 5-10 sec
#

CLUSTER_DF_PATH = '../data/sample/cluster_test_data_all_clusters_300.csv'
CENSUS_GEOM_PATH = '../data/shape_data/all_census_tract_shapes.json.gz'

# read cluster data
CLUSTER_DF = pd.read_csv(CLUSTER_DF_PATH)

# read shape data
with gzip.GzipFile(CENSUS_GEOM_PATH, 'r') as f:
    TRACT_ALL = json.loads(f.read().decode('utf-8'))
GPDF = gp.GeoDataFrame.from_features(TRACT_ALL['features'])
print(GPDF.GEOID.values)
################################################################################
mapboxt = open(".mapbox_token").read().rstrip()
####
DEV_MAP=True
####



def geoid_to_cluster(geoid, lat, lon):
    '''
    Given geoid, find the cluster associated with the matching GEOID in
    CLUSTER_DF.
    If there is not an exact match, try the method to replace the last two
    of the GEOID with 0's. This gets rid of sub-tracts that may be returned.
    Failing that, use the latitude and longitude to locate the nearest census
    tract
    '''
    # Ideal case, where we match a geoid
    attempt_1 = CLUSTER_DF[CLUSTER_DF.GEOID.astype(int)==int(geoid)]
    if attempt_1.shape[0] > 0:
        if attempt_1.shape[0] > 1: # this should not happen
            print('POSSIBLE ERROR:::Multiple Matching Clusters')
        return attempt_1['cluster'].values[0]
    
    # if unable to return earlier, try replacing last 2 digits with 0's and
    # check again
    attempt_2 = CLUSTER_DF[CLUSTER_DF.GEOID.astype(int)==int(str(geoid)[:-2]+'00')]
    if attempt_2.shape[0] > 0:
        if attempt_2.shape[0] > 1: # this should not happen
            print('POSSIBLE ERROR:::Multiple Matching Clusters')
        return attempt_2['cluster'].values[0]    

    # find nearest cluster via lat/long
    raise NotImplementedError('Need to implement nearest census tract code.')


def create_figure(geoid, lat, lon):
    n_top = 3
    geoid = 42003451102
    lat = 40.5218403
    lon = -80.1969462

    # find the cluster associated with the given geoid
    cluster = geoid_to_cluster(geoid=geoid, lat=lat, lon=lon)

    # subset df to chosen cluster
    df_subset = CLUSTER_DF[CLUSTER_DF.cluster==cluster]

    ### FIX ME - need to add rank prior to this function
    import random
    rankings_ = list(range(1, len(df_subset)+1))
    random.shuffle(rankings_)
    df_subset.loc[:, 'ranking'] = rankings_
    ###

    # Filter to highest rank
    df_subset_top = df_subset[df_subset.ranking<=n_top]
    df_subset_other = df_subset[df_subset.ranking>n_top]


    # subset the geopandas dataframe to geoids that match with the current clusters
    gpdf_subset = GPDF[GPDF.GEOID.astype(int).isin(df_subset.GEOID.astype(int))]
    # convert the filtered geopandas dataframe to geojson
    gpdf_subset_json = json.loads(gpdf_subset.to_json())
    # update the ids in the geojson so that they are the census tract geoids
    def update_ids(json_obj):
        for i, feature in enumerate(json_obj['features']):
            json_obj['features'][i]['id'] = int(feature['properties']['GEOID'])
        return json_obj
    gpdf_subset_json = update_ids(gpdf_subset_json)

    # draw the census tracts
    fig = go.Figure(
    go.Choroplethmapbox(
        uid='choro',
        geojson=gpdf_subset_json,
        featureidkey='properties.GEOID',
        locations=df_subset.GEOID,
        # coloring
        z=df_subset.ranking,
        zmin=df_subset.ranking.min(),
        zmax=df_subset.ranking.max(),
        colorscale=[[0, 'rgb(47, 158, 168)'], [1,'rgb(47, 158, 168)']],
        showscale=False, # True for color bar scale
        # opacity and line width
        marker_opacity=.3,
        marker_line_width=1,
        # hover text
        text=df_subset.NAME,
        )
    )


    # add a 0 margin
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


    # add top tract points- this makes it easier to find matches when zoomed out
    fig = fig.add_scattermapbox(
        mode='markers+text',
        lat=df_subset_top['INTPTLAT'],
        lon=df_subset_top['INTPTLONG'],
        marker={'size': 25,
                'symbol': 'circle',
                'color': 'yellow',
                'opacity':.8,
                'allowoverlap': True,
               },
        text=['{}'.format(x) for x in df_subset_top.ranking.values.tolist()],
        hovertemplate='Rank: %{text}<extra></extra>',
        showlegend=False,
        below="''",
    )

    # Font style
    fig.update_layout(
        font=dict(
            family="Courier New, monospace",
            size=25,
            color="Black"
        )
    )


    # add all tract points not in top, make them smaller
    fig = fig.add_scattermapbox(
        mode='markers',
        lat=df_subset_other['INTPTLAT'],
        lon=df_subset_other['INTPTLONG'],
        marker={'size': 10,
                'symbol': 'circle',
                'color': 'lightblue',
                'opacity':0.3,
                'allowoverlap': True,
               },
        text=list(map(str, df_subset_other.ranking.values.tolist())),
        hoverinfo='text',
        hovertemplate='Rank: %{text}<extra></extra>',
        #hovertext=list(map(str, df_subset_other.ranking.values.tolist())),
        showlegend=False,
        #hoverinfo='none',
        below=0,
    )

    if not DEV_MAP:
        # add a map layer
        fig.update_layout(
            #mapbox_style="open-street-map",
            #mapbox_style='carto-positron',
            mapbox=dict(
                bearing=0,
                center=dict(
                    lat=38,
                    lon=-94
                ),
                pitch=0,
                zoom=3,
                accesstoken=mapboxt,
                #style='open-street-map',
                style='light',
                #style='satellite-streets',
            ),
            showlegend=False
        )
    else:
        # add a map layer
        fig.update_layout(
            #mapbox_style="open-street-map",
            #mapbox_style='carto-positron',
            mapbox=dict(
                bearing=0,
                center=dict(
                    lat=38,
                    lon=-94
                ),
                pitch=0,
                zoom=3,
                #accesstoken=mapboxt,
                style='carto-positron',
                #style='light',
                #style='satellite-streets',
            ),
            showlegend=False
        )

    import copy
    zoom_figures = []
    for idx, row in df_subset_top.sort_values('ranking').iterrows():
        zoom_figures.append(
            update_map(copy.deepcopy(fig), zoom=10, lat=row.INTPTLAT, lon=row.INTPTLONG)
        )

    return fig, zoom_figures

def update_map(fig, zoom, lat=None, lon=None):
    '''
    For a given figure fig, update the zoom level.
    If both lat and lon are also provided, move the camera to that location.
    '''
    if not lat or not lon:
        return fig.update_layout(mapbox_zoom=zoom)
    else:
        return fig.update_layout(
            mapbox_zoom=zoom,
            mapbox_center = {"lat": lat, "lon": lon}
        )

