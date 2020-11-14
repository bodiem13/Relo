from flask import Flask, render_template


app = Flask(__name__)
app.debug = True


import clustervis



@app.route('/')
def index():


    # create figure + zoomed-in top figures
    fig, zoom_figures = clustervis.create_figure(
        geoid=10003014702,
        lat=39.6536026,
        lon=-75.7418482
    )
    
    # figure to json
    figJSON = fig.to_json()

    # create top 3 location maps
    figJSON1 = zoom_figures[0].to_json()
    figJSON2 = zoom_figures[1].to_json()
    figJSON3 = zoom_figures[2].to_json()
    



    # CREATE 4 versions of the figure:
    # 1. Full map with pins
    # 2-4. Zoomed in on each of top 3 picks.
    # pass all to flask. show 1 by default. bind the other 3 to buttons.

    return render_template('vis_development_index.html',
                           divID='mymap',
                           figJSON=figJSON,
                           figJSON1=figJSON1,
                           figJSON2=figJSON2,
                           figJSON3=figJSON3,
                           )









if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
