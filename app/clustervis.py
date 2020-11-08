import time
import gzip
import json
import copy
import plotly
import plotly.graph_objects as go

import geopandas as gp
import pandas as pd
import numpy as np
import scipy.spatial as spatial
from geopy.geocoders import Nominatim

pd.options.mode.chained_assignment = None  # default='warn'


################################################################################
# OPTIONS
mapboxt = open(".mapbox_token").read().rstrip()
####
DEV_MAP=True
DEV_IGNORE_CLUSTER_MATCHING=False
AMENITIES_DRAW_DISTANCE = 25 # 2, 5, 10, 25, or 50 miles
####

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
GAZ_PATH = '../data/gaz/2018_5yr_cendatagov_GAZ_v4.pkl'
AMENITIES_PATH = '../data/amenities/amenities_full.pkl.gz'
AMENITIES_25_PATH = '../data/amenities/amenities_25mi_for_vis.pkl.gz'
FEATURE_DATA_PATH = '../data/features/Final_Visualization_Input_Data.pkl'

start = time.time()
print('Loading clustervis.py module-level globals (this may take a moment)')
print('---> Reading and preparing amenities data')
if AMENITIES_DRAW_DISTANCE != 25:
    AMENITIES = pd.read_pickle(AMENITIES_PATH, compression='gzip')
    # subset to geoid + the fields that contain indexes of the amenities
    amenity_list_cols = [x for x in AMENITIES.columns if x.startswith('LIST') and\
                         x.endswith('{}'.format(AMENITIES_DRAW_DISTANCE))]
    cols = ['GEOID'] + amenity_list_cols
    AMENITIES = AMENITIES[cols]
else:
    AMENITIES = pd.read_pickle(AMENITIES_25_PATH, compression='gzip')
    amenity_list_cols = [x for x in AMENITIES if x != 'GEOID']
AMENITY_REFERENCE = {x: pd.read_pickle('../data/amenities/dataframes/{}.pkl'.format(x)) for x in [y.split('_')[1] for y in amenity_list_cols]}
print('------> Done')

print('---> Reading cluster output')
# read cluster data
CLUSTER_DF = pd.read_csv(CLUSTER_DF_PATH)
print('------> Done')

print('---> Reading geometry data')
# read shape data
with gzip.GzipFile(CENSUS_GEOM_PATH, 'r') as f:
    TRACT_ALL = json.loads(f.read().decode('utf-8'))
GPDF = gp.GeoDataFrame.from_features(TRACT_ALL['features'])
print('------> Done')

print('---> Reading Gaz data and building KD-Tree')
# Read Gaz data. Create kd-tree of points in order to find nearest cluster
# when exact geoid match cannot be found.
GAZ = pd.read_pickle(GAZ_PATH)
GAZ.columns = [x.strip() for x in GAZ.columns]
points = []
for i, row in GAZ.iterrows():
    points.append([row.INTPTLAT, row.INTPTLONG])
points = np.array(points)
CLUSTER_POINT_TREE = spatial.cKDTree(points)
print('------> Done')

print('---> Reading Features (for table comparisons)')
ORIG_FEATURE_DATA = pd.read_pickle(FEATURE_DATA_PATH)
ORIG_FEATURE_DATA['GEOID'] = ORIG_FEATURE_DATA['GEOID'].astype(int)
print('------> Done')

print('Done. {} seconds to load.'.format(round(time.time()-start, 2)))
################################################################################
################################################################################
################################################################################


        
################################################################################        

class ClusterVis:
    def __init__(self, geoid=42003451102, lat=40.5218403, lon=-80.1969462, n_top=3):
        try:
            if geoid is not None:
                self.geoid = int(geoid)
            else:
                self.geoid = None
            self.n_top = int(n_top)
            # lat and lon for fallback closest geoid/cluster matching
            self.lat = float(lat)
            self.lon = float(lon)
        except ValueError:
            print('geoid and n_top must be int-like, lat/lon must be float-like')
        
        self.fig = None
        self.zoom_figures = []
        


        # get the cluster        
        self.cluster = self.geoid_to_cluster()

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
        # draw amenities around top points
        self._add_amenities()
        # add the 'other' subset of points
        # these have a smaller, different style than the top matches
        self._add_other_points()
        # add the point that was searched for
        self._add_original_point()
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

    
    def _add_amenities(self):
        # get geoids of top rankings within cluster
        top_geoids = self.df_subset_top.GEOID.astype(int).values.tolist()
        # iterate over AMENITIES fields != to geoid
        # pull out that field (list of indicies corresponding to 
        # AMENITY_REFERENCE tables). select those indicies (if they exist)
        # and plot those amenities
        styling = {
            'GROCERY': {'color': 'orange', 'name': 'Grocery Store'},
            'GYMS': {'color': 'darkblue', 'name': 'Gym'},
            'HARDWARE': {'color': 'brown', 'name': 'Hardware Store'},
            'MEDICAL': {'color': 'pink', 'name': 'Medical Facility'},
            'PARKS': {'color': 'lightgreen', 'name': 'Park'},
        }
        
        
        for col in AMENITIES.columns:
            if col == 'GEOID':
                continue
            
            name = col.split('_')[1]
            current_amenity_results = pd.DataFrame()    
            for gid in top_geoids:
                am_sub = AMENITIES[AMENITIES.GEOID.astype(int)==gid]
                # get list of amenity indexes for the current type of amenity `name`
                amenities_list = am_sub[col].values[0]
                if amenities_list: # some are empty, so do this check
                    # do a lookup in AMENITY_REFERENCE to get the lat/lon and other info
                    amenity_data = AMENITY_REFERENCE[name].iloc[amenities_list]
                    current_amenity_results = pd.concat([current_amenity_results, amenity_data])
            #print(current_amenity_results)
            
            # add the amenity points
            self.fig = self.fig.add_scattermapbox(
                uid=name,
                mode='markers',
                lat=current_amenity_results['lat_cleaned'],
                lon=current_amenity_results['lon_cleaned'],
                marker={'size': 7,
                        'symbol': 'circle',
                        'color': styling[name]['color'],
                        'opacity':0.6,
                        'allowoverlap': True,
                       },
                text=['{}: {}'.format(styling[name]['name'], x) for x in current_amenity_results['name'].values.tolist()],
                hoverinfo='text',
                hovertemplate='%{text}<extra></extra>',
                showlegend=True,
                name=styling[name]['name'],
                #labels=name,
            )

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
            hovertemplate='%{text}<extra></extra>',
            )
        )        

    def _add_other_points(self):
        # add all tract points not in top, make them smaller
        self.fig = self.fig.add_scattermapbox(
            uid='other',
            mode='markers',
            lat=self.df_subset_other['INTPTLAT'],
            lon=self.df_subset_other['INTPTLONG'],
            marker={'size': 15,
                    'symbol': 'circle',
                    'color': 'lightblue',
                    'opacity':0.3,
                    'allowoverlap': True,
                   },
            text=list(map(str, self.df_subset_other.ranking.values.tolist())),
            hoverinfo='text',
            hovertemplate='Rank: %{text}<extra></extra>',
            name='Other Matching Neighborhoods'
            #hovertext=list(map(str, df_subset_other.ranking.values.tolist())),
            #showlegend=False,
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
            name='Top Matched Neighborhoods'
            #showlegend=False,
            #below="''",
        )
        
        # Font style
#        self.fig.update_layout(
#            font=dict(
#                family="Courier New, monospace",
#                size=25,
#                color="Black"
#            )
#        )

    def _add_original_point(self):
         self.fig = self.fig.add_scattermapbox(
            uid='original',
            mode='markers',
            lat=[self.lat],
            lon=[self.lon],
            marker={'size': 25,
                    'symbol': 'circle',
                    'color': 'green',
                    'opacity':.7,
                    'allowoverlap': True,
                   },
            text=['Searched point'],
            hovertemplate='%{text}<extra></extra>',
            name='Searched Neighborhood'
            #showlegend=False,
            #below="''",
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
            #showlegend=False
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

    def geoid_to_cluster(self):
        '''
        Given geoid, find the cluster associated with the matching GEOID in
        CLUSTER_DF.
        If there is not an exact match, try the method to replace the last two
        of the GEOID with 0's. This gets rid of sub-tracts that may be returned.
        Failing that, use the latitude and longitude to locate the nearest census
        tract
        If no geoid originally passed, update with geoid of closest matching cluster
        '''
        if self.geoid is not None:
            # Ideal case, where we match a geoid
            try:
                attempt_1 = CLUSTER_DF[CLUSTER_DF.GEOID.astype(int)==self.geoid]
                if attempt_1.shape[0] > 0:
                    if attempt_1.shape[0] > 1: # this should not happen
                        print('POSSIBLE ERROR:::Multiple Matching Clusters')
                    return attempt_1['cluster'].values[0]
            except Exception as e:
                print('Attempt 1: {}'.format(e))
            
            # if unable to return earlier, try replacing last 2 digits with 0's and
            # check again
            try:
                attempt_2 = CLUSTER_DF[CLUSTER_DF.GEOID.astype(int)==int(str(self.geoid)[:-2]+'00')]
                if attempt_2.shape[0] > 0:
                    if attempt_2.shape[0] > 1: # this should not happen
                        print('POSSIBLE ERROR:::Multiple Matching Clusters')
                    return attempt_2['cluster'].values[0]    
            except Exception as e:
                print('Attempt 2: {}'.format(e))
                
        # find nearest cluster via lat/long
        #raise NotImplementedError('Need to implement nearest census tract code.')
        closest_point = CLUSTER_POINT_TREE.query([self.lat, self.lon], 1)
        closest_point_index = closest_point[1]
        geoid_match = int(GAZ.iloc[closest_point_index].GEOID)
        self.geoid = geoid_match # update geoid if we're using this fallback
        attempt_3 = CLUSTER_DF[CLUSTER_DF.GEOID.astype(int)==geoid_match]
        if attempt_3.shape[0] > 0:
            if attempt_3.shape[0] > 1: # this should not happen
                print('POSSIBLE ERROR:::Multiple Matching Clusters')
            return attempt_3['cluster'].values[0]
            
    def build_tables(self):
        """Build tables for HTML template, to show original search vs. top match & percent change"""
        top_geoids = self.df_subset_top.sort_values('ranking').GEOID.astype(int).values.tolist()
        original_geoid = int(self.geoid)
        
        origFD = ORIG_FEATURE_DATA[ORIG_FEATURE_DATA.GEOID==original_geoid]
        top1FD = ORIG_FEATURE_DATA[ORIG_FEATURE_DATA.GEOID==top_geoids[0]]
        top2FD = ORIG_FEATURE_DATA[ORIG_FEATURE_DATA.GEOID==top_geoids[1]]
        top3FD = ORIG_FEATURE_DATA[ORIG_FEATURE_DATA.GEOID==top_geoids[2]]
        
        non_numeric_cols = ['NAME', 'GEOID', 'GEO_ID','INTPTLAT', 'INTPTLONG']
        
        table = pd.concat([origFD, top1FD, top2FD, top3FD]).reset_index(drop=True)
        non_num_table = table[non_numeric_cols].T.copy()
        non_num_table.columns = ['c0', 'c1', 'c2', 'c3']
        table = table.drop(columns=non_numeric_cols)
        table = table.T
        table.columns = ['c0', 'c1', 'c2', 'c3']

       
        print('Calculating % change....')
        for col in ['c1', 'c2', 'c3']:
            table['c0_{}'.format(col)] = ((table[col] - table.c0) / table.c0 * 100.).round(1)
        
        print('Sorting and dealing with missing values...')
        # sort by absolute value of the percent change
        t0 = table[['c0']]
        t1 = table[['c0', 'c1', 'c0_c1']].fillna(9999999999).reindex(table['c0_c1'].abs().sort_values().index).replace(9999999999, '--')
        t2 = table[['c0', 'c2', 'c0_c2']].fillna(9999999999).reindex(table['c0_c2'].abs().sort_values().index).replace(9999999999, '--')
        t3 = table[['c0', 'c3', 'c0_c3']].fillna(9999999999).reindex(table['c0_c3'].abs().sort_values().index).replace(9999999999, '--')
        
        print('Merging back non-numeric data...')
        # add back the non-numeric fields at the front and reset index
        t0 = pd.concat([non_num_table[['c0']], t0]).fillna('--').reset_index()
        t1 = pd.concat([non_num_table[['c0', 'c1']], t1]).fillna('--').reset_index()
        t2 = pd.concat([non_num_table[['c0', 'c2']], t2]).fillna('--').reset_index()
        t3 = pd.concat([non_num_table[['c0', 'c3']], t3]).fillna('--').reset_index()

        print('Renaming Fields...')
        # rename fields
        t0.columns = ['Feature', 'Searched Neighborhood']
        t1.columns = ['Feature', 'Searched Neighborhood', 'Top 1st Match', 'Percent Change']
        t2.columns = ['Feature', 'Searched Neighborhood', 'Top 2nd Match', 'Percent Change']
        t3.columns = ['Feature', 'Searched Neighborhood', 'Top 3rd Match', 'Percent Change']                
        
        print('Finished generating tables.')

        return t0, t1, t2, t3


    def get_top_city_names(self):
        top = self.df_subset_top.sort_values('ranking').copy().reset_index(drop=True)
        
        # by default, use census tract names for neighborhoods
        results = {
            't1': {'tract': top.iloc[0].NAME, 'loc': None, 'neighborhood': '', 'citystate': top.iloc[0].NAME},
            't2': {'tract': top.iloc[1].NAME, 'loc': None, 'neighborhood': '', 'citystate': top.iloc[1].NAME},
            't3': {'tract': top.iloc[2].NAME, 'loc': None, 'neighborhood': '', 'citystate': top.iloc[2].NAME},
        }
        
        # do a lookup for a more specific address
        
        for i, key in enumerate(['t1', 't2', 't3']):
            try:
                geolocator = Nominatim(user_agent="my_application")
                loc = geolocator.reverse((top.iloc[i].INTPTLAT, top.iloc[i].INTPTLONG))
                results[key]['loc'] = loc.raw['address']
                
                for spelling in ['neighbourhood', 'neighborhood', 'neighboorhood', 'suburb', 'hamlet', 'town', 'street']:
                    if spelling in results[key]['loc'].keys():
                        results[key]['neighborhood'] = results[key]['loc'][spelling]
                        break
                    else:
                        print(list(results[key]['loc'].keys()))

                    
                if 'city' in results[key]['loc'].keys() and 'state' in results[key]['loc'].keys():
                    results[key]['citystate'] = '{}, {}'.format(results[key]['loc']['city'], results[key]['loc']['state'])
            except Exception as e:
                print(e)

                   
        return results
               
        

        
        
             
