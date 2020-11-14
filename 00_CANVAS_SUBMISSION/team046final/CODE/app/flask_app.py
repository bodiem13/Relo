# Steps to run
# Do not start a local server. This can be ran locally and viewed on http://localhost:5000/
# If server appears busy, run ps -fA | grep python (this will show open connections)
# Use kill ##### command to end connections

# render template function allows use of html templates
from flask import Flask, render_template, request, jsonify, redirect, url_for, Markup
from geopy.geocoders import Nominatim
import censusgeocode as cg

# generated via http://patorjk.com/software/taag/#p=testall&f=Epic&t=RELO%20APP
print(
"""
###################################
#██████╗ ███████╗██╗      ██████╗ #
#██╔══██╗██╔════╝██║     ██╔═══██╗#
#██████╔╝█████╗  ██║     ██║   ██║#
#██╔══██╗██╔══╝  ██║     ██║   ██║#
#██║  ██║███████╗███████╗╚██████╔╝#
#╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ #
###################################
"""
)

import clustervis

app = Flask(__name__)
address = str()

# global to hold most recent results
# specifies defaults if error in address matching
# have a default lat/lon as fallback
MOST_RECENT_RESULTS = {"geoid": None, "lat": 40.5218403, "lon": -80.1969462}


def get_coordinates(address):
    """Given a string address, use geolocator api to get address info,
       including lat/lon of searched location.
    """
    try:
        geolocator = Nominatim(user_agent="my_application")
        loc = geolocator.geocode(str(address))
        print(loc.address)
        full_address = loc.address
        latitude = float(loc.latitude)
        longitude = float(loc.longitude)
        return [longitude, latitude], full_address
    except:
        return None


@app.route("/")
def render_index():
    return render_template("index.html")


@app.route("/home")
def return_home():
    return render_template("index.html")


@app.route("/search_results", strict_slashes=False, methods=["GET", "POST"])
def search_results():
    # if POST request, update MOST_RECENT_RESULTS
    if request.method == "POST":
        print("search_results called as POST")
        address = request.form["address"]
        MOST_RECENT_RESULTS["address"] = address

        # Get the coordinates (lon/lat) and address for given user search.
        coordinates, full_address = get_coordinates(address)
        print("Currently viewing results for: ", full_address)
        if coordinates:
            print("COORDS FOUND: {}".format(coordinates))
            MOST_RECENT_RESULTS["search_lon"] = coordinates[0]
            MOST_RECENT_RESULTS["search_lat"] = coordinates[1]
            MOST_RECENT_RESULTS["geoid"] = None # geoid identification is now done within clustervis
        else: # fallback to default example
            pass


        # build visualization object
        # geoid may be passed as None. If so, fallback mechanism will take
        # place to determine the "home" neighborhood.
        cvis = clustervis.ClusterVis(
            geoid=MOST_RECENT_RESULTS["geoid"],
            lat=MOST_RECENT_RESULTS["search_lat"],
            lon=MOST_RECENT_RESULTS["search_lon"],
        )
        
        # Create 4 maps, the overview (high level) map, and 3 zoomed figures
        # corresponding to the top 3 matches
        overview, zoom_figures = cvis.create_figures()

        # send figures to json and store in the state variable
        MOST_RECENT_RESULTS["fig0"] = overview.to_json()
        MOST_RECENT_RESULTS["fig1"] = zoom_figures[0].to_json()
        MOST_RECENT_RESULTS["fig2"] = zoom_figures[1].to_json()
        MOST_RECENT_RESULTS["fig3"] = zoom_figures[2].to_json()

        # Build html tables for display
        t0, t1, t2, t3 = cvis.build_tables()
        MOST_RECENT_RESULTS["t0"] = t0.to_json(orient="index")
        MOST_RECENT_RESULTS["t1"] = t1.to_json(orient="index")
        MOST_RECENT_RESULTS["t2"] = t2.to_json(orient="index")
        MOST_RECENT_RESULTS["t3"] = t3.to_json(orient="index")

        # Attempt to get names of the city, state, and neighborhood
        top_city_names = cvis.get_top_city_names()
        MOST_RECENT_RESULTS["name1"] = top_city_names["t1"]["citystate"]
        MOST_RECENT_RESULTS["name2"] = top_city_names["t2"]["citystate"]
        MOST_RECENT_RESULTS["name3"] = top_city_names["t3"]["citystate"]
        MOST_RECENT_RESULTS["subname1"] = top_city_names["t1"]["neighborhood"]
        MOST_RECENT_RESULTS["subname2"] = top_city_names["t2"]["neighborhood"]
        MOST_RECENT_RESULTS["subname3"] = top_city_names["t3"]["neighborhood"]

        # Get the latitude/longitude of the home census tract.
        top_match_coords = cvis.get_top_match_coords()
        MOST_RECENT_RESULTS["c1"] = top_match_coords[0]
        MOST_RECENT_RESULTS["c2"] = top_match_coords[1]
        MOST_RECENT_RESULTS["c3"] = top_match_coords[2]

    return render_template(
        "test.html",
        address=MOST_RECENT_RESULTS["address"],
        fig0=MOST_RECENT_RESULTS["fig0"],
        fig1=MOST_RECENT_RESULTS["fig1"],
        fig2=MOST_RECENT_RESULTS["fig2"],
        fig3=MOST_RECENT_RESULTS["fig3"],
        t0=MOST_RECENT_RESULTS["t0"],
        t1=MOST_RECENT_RESULTS["t1"],
        t2=MOST_RECENT_RESULTS["t2"],
        t3=MOST_RECENT_RESULTS["t3"],
        name1=MOST_RECENT_RESULTS["name1"],
        name2=MOST_RECENT_RESULTS["name2"],
        name3=MOST_RECENT_RESULTS["name3"],
        subname1=MOST_RECENT_RESULTS["subname1"],
        subname2=MOST_RECENT_RESULTS["subname2"],
        subname3=MOST_RECENT_RESULTS["subname3"],
        c1=MOST_RECENT_RESULTS["c1"],
        c2=MOST_RECENT_RESULTS["c2"],
        c3=MOST_RECENT_RESULTS["c3"],
    )


@app.route("/about")
def render_about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, use_reloader=False, debug=True)

