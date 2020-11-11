# Steps to run
# Do not start a local server. This can be ran locally and viewed on http://localhost:5000/
# If server appears busy, run ps -fA | grep python (this will show open connections)
# Use kill ##### command to end connections

# render template function allows use of html templates
from flask import Flask, render_template, request, jsonify, redirect, url_for, Markup
from geopy.geocoders import Nominatim
import censusgeocode as cg

import clustervis

app = Flask(__name__)
address = str()

# global to hold most recent results
# specifies defaults if error in address matching
MOST_RECENT_RESULTS = {"geoid": 42003451102, "lat": 40.5218403, "lon": -80.1969462}

# function can be used to get latitude longitude from address instead of returning address
# def get_user_input(address):
#    return address


def get_coordinates(address):
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


def get_tract(coordinates):
    try:
        lon, lat = coordinates
        lon, lat = round(lon, 5), round(lat, 5)
        print(lon, lat)
        result = cg.coordinates(x=lon, y=lat)
        print("GET_TRACT RESULT: {}".format(result))
        tract_info = result["Census Tracts"][0]
        return tract_info
    except Exception as e:
        print("===COULD NOT IDENTIFY TRACT -- Falling Back===")
        print(e)
        return None


@app.route("/")
def render_index():
    return render_template("index.html")


@app.route("/home")
def return_home():
    return render_template("index.html")


# @app.route("/results")
# def render_result():
#    return render_template("test.html")


@app.route("/search_results", strict_slashes=False, methods=["GET", "POST"])
def search_results():
    # if POST request, update MOST_RECENT_RESULTS
    if request.method == "POST":
        print("search_results called as POST")
        address = request.form["address"]

        coordinates, full_address = get_coordinates(address)
        print("Currently viewing results for: ", full_address)
        if coordinates:
            print("COORDS FOUND: {}".format(coordinates))
            MOST_RECENT_RESULTS["lon"] = coordinates[0]
            MOST_RECENT_RESULTS["lat"] = coordinates[1]
            MOST_RECENT_RESULTS["geoid"] = None
            tract = get_tract(coordinates)
            if tract:
                print("TRACT FOUND: {}".format(tract))
                try:
                    MOST_RECENT_RESULTS["lat"] = float(tract["INTPTLAT"])
                    MOST_RECENT_RESULTS["lon"] = float(tract["INTPTLON"])
                    MOST_RECENT_RESULTS["geoid"] = int(tract["GEOID"])
                except Exception as e:
                    print(e, "COULD NOT ASSIGN tract RESULTS")
            else:
                print("FALLING BACK TO FINDING CLOSEST TRACT")
        else:
            print("Using latest (and/or default demo) tract")

        # cvis = clustervis.ClusterVis(geoid=42003451102, lat=40.5218403, lon=-80.1969462, n_top=3)
        print("CURRENT GEOID BEING USED: {}".format(MOST_RECENT_RESULTS["geoid"]))
        cvis = clustervis.ClusterVis(
            geoid=MOST_RECENT_RESULTS["geoid"],
            lat=MOST_RECENT_RESULTS["lat"],
            lon=MOST_RECENT_RESULTS["lon"],
            n_top=3,
        )
        overview, zoom_figures = cvis.create_figures()

        # figure to json
        fig0 = overview.to_json()

        # create top 3 location maps
        fig1 = zoom_figures[0].to_json()
        fig2 = zoom_figures[1].to_json()
        fig3 = zoom_figures[2].to_json()

        MOST_RECENT_RESULTS["fig0"] = fig0
        MOST_RECENT_RESULTS["fig1"] = fig1
        MOST_RECENT_RESULTS["fig2"] = fig2
        MOST_RECENT_RESULTS["fig3"] = fig3

        # Build html tables for display
        t0, t1, t2, t3 = cvis.build_tables()
        MOST_RECENT_RESULTS["t0"] = t0.to_json(orient="index")
        MOST_RECENT_RESULTS["t1"] = t1.to_json(orient="index")
        MOST_RECENT_RESULTS["t2"] = t2.to_json(orient="index")
        MOST_RECENT_RESULTS["t3"] = t3.to_json(orient="index")

        top_city_names = cvis.get_top_city_names()
        MOST_RECENT_RESULTS["name1"] = top_city_names["t1"]["citystate"]
        MOST_RECENT_RESULTS["name2"] = top_city_names["t2"]["citystate"]
        MOST_RECENT_RESULTS["name3"] = top_city_names["t3"]["citystate"]
        MOST_RECENT_RESULTS["subname1"] = top_city_names["t1"]["neighborhood"]
        MOST_RECENT_RESULTS["subname2"] = top_city_names["t2"]["neighborhood"]
        MOST_RECENT_RESULTS["subname3"] = top_city_names["t3"]["neighborhood"]

    return render_template(
        "test.html",
        address=address,
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
    )


@app.route("/about")
def render_about():
    "Hello {}!".format("Mike")

    return render_template("about.html")


# @app.route("/userinput", methods=["GET", "POST"])
# def post_user_inputs():
#    address = request.form["address"]
#    word = request.args.get("address")
#    coordinates = get_coordinates(address)
#    tract = get_tract(coordinates)
#    result = {}
#    result["longitude"] = coordinates[0]
#    result["latitude"] = coordinates[1]
#    result["tract"] = tract

#    # this line may be repetitive but was needed to get the results into HTML initially. Have not tried to remove yet.
#    result = {str(key): value for key, value in result.items()}
#    print(result)
#    #render_search_results(location=result)
#    #return jsonify(result=result)
#    result = jsonify(result=result)
#    return redirect(url_for('search_results', location=result))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, use_reloader=False, debug=True)

