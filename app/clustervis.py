import gzip
import json
import copy
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
DEV_IGNORE_CLUSTER_MATCHING=True
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


class ClusterVis:
    def __init__(self, geoid=42003451102, n_top=3):
        try:
            self.geoid = int(geoid)
            self.n_top = int(n_top)
        except ValueError:
            print('geoid and n_top must be int-like')
        
        self.fig = None
        self.zoom_figures = []
        
        ### TESTING
        self.lat = 40.5218403
        self.lon = -80.1969462
        
        if not DEV_IGNORE_CLUSTER_MATCHING:
            self.cluster = geoid_to_cluster(self.geoid, self.lat, self.lon)
        else:
            print('DEV MODE ENABLED. CLUSTER NOT CALCULATED FROM INPUT')
            self.cluster = 5

        # subset CLUSTER_DF to matching cluster
        self.df_subset = CLUSTER_DF[CLUSTER_DF.cluster==self.cluster]


        ### FIX ME - need to add rank prior to this function
        print('WARNING::::STILL NEED TO INTEGRATE RANKING DATA')
        import random
        rankings_ = list(range(1, len(self.df_subset)+1))
        random.shuffle(rankings_)
        self.df_subset.loc[:, 'ranking'] = rankings_
        ###

        # get top matches
        self.df_subset_top = self.df_subset[self.df_subset.ranking<=self.n_top]
        # get non-top matches
        self.df_subset_other = self.df_subset[self.df_subset.ranking>self.n_top]
        # subset geopandas to matching geoids
        self.gpdf_subset_json = self._prepare_geopandas_subset()

          
        
    def create_figures(self):
        """
        Create overview figure and figures zoomed on the top matches
        Methods called in this pipeline should update self.fig
        """
        # draw map and census tracts
        self._create_initial_map_figure()
        # update figure margin
        self.fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        # add the 'other' subset of points
        # these have a smaller, different style than the top matches
        self._add_other_points()
        # add 'top' subset of points
        self._add_top_points()
        # add map style
        if not DEV_MAP:
            self._add_map_style()
        else:
            self._add_map_style(dev=True)
        # generate zoomed-in figures of top matches
        self._generate_zoomed_figures()

        return self.fig, self.zoom_figures


    def _create_initial_map_figure(self):
        # draw the census tracts
        self.fig = go.Figure(
        go.Choroplethmapbox(
            uid='choro',
            geojson=self.gpdf_subset_json,
            featureidkey='properties.GEOID',
            locations=self.df_subset.GEOID,
            # coloring
            z=self.df_subset.ranking,
            zmin=self.df_subset.ranking.min(),
            zmax=self.df_subset.ranking.max(),
            colorscale=[[0, 'rgb(47, 158, 168)'], [1,'rgb(47, 158, 168)']],
            showscale=False, # True for color bar scale
            # opacity and line width
            marker_opacity=.3,
            marker_line_width=1,
            # hover text
            text=self.df_subset.NAME,
            )
        )        

    def _add_other_points(self):
        # add all tract points not in top, make them smaller
        self.fig = self.fig.add_scattermapbox(
            uid='other',
            mode='markers',
            lat=self.df_subset_other['INTPTLAT'],
            lon=self.df_subset_other['INTPTLONG'],
            marker={'size': 10,
                    'symbol': 'circle',
                    'color': 'lightblue',
                    'opacity':0.3,
                    'allowoverlap': True,
                   },
            text=list(map(str, self.df_subset_other.ranking.values.tolist())),
            hoverinfo='text',
            hovertemplate='Rank: %{text}<extra></extra>',
            #hovertext=list(map(str, df_subset_other.ranking.values.tolist())),
            showlegend=False,
            #hoverinfo='none',
            #below='top',
        )

    def _add_top_points(self):
        # add top tract points- this makes it easier to find matches when zoomed out
        self.fig = self.fig.add_scattermapbox(
            uid='top',
            mode='markers+text',
            lat=self.df_subset_top['INTPTLAT'],
            lon=self.df_subset_top['INTPTLONG'],
            marker={'size': 25,
                    'symbol': 'circle',
                    'color': 'yellow',
                    'opacity':.8,
                    'allowoverlap': True,
                   },
            text=['{}'.format(x) for x in self.df_subset_top.ranking.values.tolist()],
            hovertemplate='Rank: %{text}<extra></extra>',
            showlegend=False,
            #below="''",
        )
        
        # Font style
        self.fig.update_layout(
            font=dict(
                family="Courier New, monospace",
                size=25,
                color="Black"
            )
        )

    def _add_map_style(self, dev=False):
        if dev is False:
            style = 'light'
            accesstoken = mapboxt
        else:
            style = 'carto-positron'
            accesstoken = None
    
        # add a map layer
        self.fig.update_layout(
            mapbox=dict(
                bearing=0,
                center=dict(
                    lat=38,
                    lon=-94
                ),
                pitch=0,
                zoom=3,
                accesstoken=accesstoken,
                style=style,
            ),
            showlegend=False
        )

    def _generate_zoomed_figures(self):
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

        for idx, row in self.df_subset_top.sort_values('ranking').iterrows():
            self.zoom_figures.append(
                update_map(copy.deepcopy(self.fig), zoom=10, lat=row.INTPTLAT, lon=row.INTPTLONG)
            )


    def _prepare_geopandas_subset(self):
        # subset the geopandas dataframe to geoids that match with the current clusters
        gpdf_subset = GPDF[GPDF.GEOID.astype(int).isin(self.df_subset.GEOID.astype(int))]
        # convert the filtered geopandas dataframe to geojson
        gpdf_subset_json = json.loads(gpdf_subset.to_json())
        # update the ids in the geojson so that they are the census tract geoids
        def update_ids(json_obj):
            for i, feature in enumerate(json_obj['features']):
                json_obj['features'][i]['id'] = int(feature['properties']['GEOID'])
            return json_obj
        return update_ids(gpdf_subset_json)



