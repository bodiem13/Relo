# Steps to run
# Do not start a local server. This can be ran locally and viewed on http://localhost:5000/
# If server appears busy, run ps -fA | grep python (this will show open connections)
# Use kill ##### command to end connections

# render template function allows use of html templates
from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
import censusgeocode as cg

import clustervis

app = Flask(__name__)
address = str()
# function can be used to get latitude longitude from address instead of returning address
def get_user_input(address):
    return address


def get_coordinates(address):
    address = address
    geolocator = Nominatim(user_agent="my_application")
    loc = geolocator.geocode(str(address))
    print(loc.address)
    latitude = loc.latitude
    longitude = loc.longitude
    coordinates = [longitude, latitude]
    return coordinates


def get_tract(coordinates):
    x = coordinates[0]
    y = coordinates[1]
    result = cg.coordinates(x=x, y=y)
    print(result)
    tract_info = result["Census Tracts"][0]
    individual_tract = tract_info.get("TRACT")
    return individual_tract


@app.route("/")
def render_index():
    return render_template("index.html")


@app.route("/results")
def render_result():
    print("Hello {}!".format("Mike"))

    return render_template("test.html")


@app.route("/search_results")
def render_t():
    print("Hello {}!".format("Mike"))

    
    cvis = clustervis.ClusterVis(geoid=42003451102, n_top=3)
    overview, zoom_figures = cvis.create_figures()
    
    # figure to json
    fig0 = overview.to_json()

    # create top 3 location maps
    fig1 = zoom_figures[0].to_json()
    fig2 = zoom_figures[1].to_json()
    fig3 = zoom_figures[2].to_json()
    

    return render_template('test.html',
                           divID='mymap',
                           fig0=fig0,
                           fig1=fig1,
                           fig2=fig2,
                           fig3=fig3,
                           )

    #return render_template("test.html")


@app.route("/about")
def render_about():
    "Hello {}!".format("Mike")

    return render_template("about.html")


@app.route("/home")
def return_home():
    "Hello {}!".format("Mike")

    return render_template("index.html")


@app.route("/userinput", methods=["GET", "POST"])
def post_user_inputs():
    address = request.form["address"]
    word = request.args.get("address")
    coordinates = get_coordinates(address)
    tract = get_tract(coordinates)
    result = {}
    result["longitude"] = coordinates[0]
    result["latitude"] = coordinates[1]
    result["tract"] = tract

    # this line may be repetitive but was needed to get the results into HTML initially. Have not tried to remove yet.
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)


if __name__ == "__main__":
    app.run(debug=True)

