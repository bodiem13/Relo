<p align="center">
  <img src="app/static/relo_logo_slogan.png" width="400" height="220">
</p>

# Description
Team Members: Amelia Bell, Michael Bodie, Aravinda Dassanayake, Joseph Janicki, Riesling Meyer, Nathan Smooha

Contents of File:
*Instructions
*Data Collection
*Data Cleaning
*Data Integration
*Analysis
*Visualization

### Instructions

Built and tested with Python version: 3.7.9

1. Install Anaconda Python Distribution
2. Run `conda create -n project python=3.7.9`
3. Run `conda activate project`
4. Run `pip install -r requirements.txt`
5. From app folder, run `python flask_app.py`

### Data Collection
#### Census Data (link)
1. The Census data used was obtained from the 5-year American Community Survey Responses for 2018 via data.census.gov. The data was found using an interface to first veiw the data table needed, then column selection was customized. All "tract" geographies were selected for all states, and the resulting data table is then downloaded into a zip folder, from with the csv can be extracted. In total eight of the tables were identified that contained columns relevant to our project for clustering and visualization.
2. Gazetteer Data: 2018 Census Gazetteer file holds geographical information necessary to doing data integration to the amenities data. This data maps the center of each census tract to a latitude and longitude coordinate, and it also includes estimates for the land and water areas in each tract. This data was gathered via a direct download from the link below, and were then prepared into geoJSON format via python. (https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2018_Gazetteer/2018_Gaz_tracts_national.zip)
3. All census data was then read into python dataframes and written to pickle files to be utilized for further data wrangling.
#### Amenities Data (link)
1. A python data script was used to make an API call to the Foursquare API. Prior to making the API calls, the code takes in a list of states (in the continental USA) and returns a list of zip codes. For each zip code, an API call is then made with the given parameters for the amenity in question. The returned data is then checked for completeness, and stored in a csv file. This is repeated for each amenity for which data is obtained.
2. Amenities Pulled: Grocery Stores, Gyms, Parks (local only, excluded state and national), Hardware Stores, Medical Facilities

### Data Cleaning
#### Census Data (link)
1. Initial Steps: Each column was evaluated for relevance, based on the column name, and initial list was narrowed down to those deemed necessary to keep. As necessary, ad-hoc histograms were created in python to evaluate the data setup, completeness, range, etc.
2. A python script was then created to read in the raw data, and a new dataframe was created for the columns that did not need further transformation. Those that required transformation (i.e. to be transformed into percentage of total) were then calculated and added to the new dataframe. Any calculation errors were then corrected and initially cleaned data was written to a pickle file for later integration with the amenities data for visualization use. The data was then evaluated for nulls, and records with high nulls were removed. The remaining data was then truncated to 3 standard deviations from the mean. Null values were then replaced with the mean and columns were evaluated for skewness. Box-Cox transformation was then performed on skewed columns, and the data was finally standardized using StandardScaler. A data profile was then created for the final dataset, and the final data was written to a pickle file for later integration with amenities data for clustering.
#### Amenities Data (link)
1. Initial Steps: Consolidated CSV file for the given amenity was loaded into OpenRefine and the latitude and longitude was truncated to be of equal length. The names of the amenities were then grouped by similar names and converted to the appropriate one. Addresses were clustered and duplicates were removed. Finally the name was evaluated in multiple ways to identify and remove any records that appeared to be different than the amenity in question.
2. Post Integration & Summarization with Census Geography Data: Steps taken via python script which reads in pickle file of amenities data. The data is initially profiled for evaluation of completeness and skewness. Finding that all columns are skewed, all zeroes are replaced with next lowest value (not including geography columns) and Box-Cox is then performed on each. The data is then standardized. Per discussion with the project team, the only columns that were deemed necessary to keep were those related to amenities within 25 miles of the center of a census tract and the GEOID. Columns deemed unnecessary for clustering are then removed, and a final profile is developed. The final dataframe is then ready for integration with the census data for clustering.

### Data Integration
#### Census Geography & Amenities
1. The amenities and census geography data are joined based on the latitude and longitude of each amenity location, which results in a count of each falling within each census tract. This is then repeated to calculate a "weighted count" of the amenity within X miles of the center of the census tract. This is done by dividing the count by X. The resulting data has the census GEOID, the central latitude and longitude for the census tract and the resulting amenity measures. The dataframe is then written to a pickle file for further data wrangling.
#### Census Data & Amenities
1. Clustering Data: Via a python script, the final cleaned, transformed, and standardized Census data pickle file is read into a dataframe. This is then merged with the final dataframe created from the cleaned, transformed, and standardized amenities data on the GEOID field. The resulting dataframe is then saved to a pickle file to be used for by the clustering algorithms.
2. Visualization Data: Via a python script, the initial cleaned census data pickle file is read into a dataframe. It is then merged with the amenities data (post integration & summarization with Census Geography Data) on the GEOID field. The final dataframe is then written to a pickle file to be used in the final visualization.

### Analysis
#### Preparation
1. Principal Component Analysis (PCA) was performed on the Census & Amenities data prepared for clustering, and transformed the data to have only 18 components, accounting for 95%  of the variability. After PCA, t-Distributed Stochastic Neighbor Embedding (t-SNE) decomposition was applied to the transformed data. t-SNE was chosen due to its being well suited for high-dimensional data, and it minimizes the divergence between two distributions. The result gave two-dimensional embeddings as features that not only allowed for better visualization of results, but also reduced time of fitting clustering algorithms.
#### Model
1. After testing multiple clustering algorithms, the best option was deemed to KMeans with 50 clusters. This was determined by looking at both algorithm and visualization performance.

### Visualization
#### Application
1. Results were visualized by a web-application created using Python Flask. Users first enter an address for an area that they know they like. It then identifies the census tract that has its center point closest to the entered address. It then gathers the cluster information in which that census tract resides. The top 3 census tracts are returned, ranked on the Euclidean distance of the features. The visualization then shows a map of the continental US with the census tracts in the same cluster, and highlights the top 3. Upon selection of results, the map will zoom into the selection and show more details on the amenities within the area. Likewise, there are feature comparisons showing how closely the results match between the searched address and the subsequent selection. 
