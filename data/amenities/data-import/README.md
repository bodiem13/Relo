
# RELO amenity data download tool

This script downloads amenities data from the Foursquare Places API and saves the list by state. Once all states' data is downloaded, the same script can be used to merge all the CSVs to a single CSV file.

  
## Pre requisites:

- Client ID and Client Secret from a verified Foursquare Developer account (a 'verified' accrount will have a daily rate limit of 99,500 API calls).

- Ensure the uszips.csv file exists in the same folder as this script

- If running in 'merge' mode, ensure that there is no consolidated.csv in the 'downloads/<TYPE>' folder already

  
## Configurations:

Please set the configuration parameters at the top of the script

- TYPE = An  identifier  for  the  amenity  data  type  being  handled.  Use  anything  you  like.

- CLIENT_ID = Foursquare  Developer  account  client  id  for  Places  API  access

- CLIENT_SECRET = Foursquare  Developer  account  client  secret  for  Places  API  access

- CATEGORY_LIST = Foursquare  venues  categories  that  need  to  be  processed.  Pick  from  https://developer.foursquare.com/docs/build-with-foursquare/categories/

- STATE_LIST = List  of  states  to  pull  data.  Default  list  has  all  states  pre-defined

  

## Usage:

Step 1 
> python process-amenities-data.py import

Step 2 
> python process-amenities-data.py merge

  
## Potential issues:

- API calls may fail and stop the data import. Run step 1 again after removing the state list up to the state that was being processed. Retain the state that failed.