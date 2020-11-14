Relo: Relocation Made Easy

Contributors: Amelia Bell, Michael Bodie, Aravinda Dassanayake, Joseph Janicki, Riesling Meyer, Nathan Smooha

CONTENTS OF THE README
---------------------

 * Description
 * Installation
 * EXECUTION



DESCRIPTION
------------

Welcome to Relo: Relocation made Easy! Relo incorporates a clustering-based approach to find the best neighborhoods to live. While utilizing census and amenities data, Relo is able to give people the confidence to relocate to a location they are sure to enjoy. 

APP DIRECTORY

The 'app' directory is used to store all code associated with the visual application for Relo. 

Inside the app directory, we have the following structure:

	The 'static' directory contains images and stylesheets used in the application. 

	The 'templates' directory contains the files used for building the front end UI. 

	Finally, the clustervis.py, flask_app.py, and vis_development_app.py files are used to run python code related to this project. 

Please refer to Diagram_1 below for more information about the structure of the 'app' directory (note the images that are stored in the 'static' directory are not included in the diagram below). 


Diagram_1
├── app/
│   ├── .vscode/
│   │       └── launch.json
│   ├── __pycache__/
│   │       └── flask_app.cpython-37.pyc
│   ├── static/
│   │   │   ├── stylesheets
│   │   │   │ 	├── index_style.css
│   │   │   │ 	├── result.css
│   │   │   │ 	└── search_form.css
│   ├── templates/
│   │       ├── about.html
│   │       ├── index.html
│   │       ├── result.html
│   │       ├── test.html
│   │       └── vis_development_index.html
│   ├── .DS_Store
│   ├── .mapbox_token
│   ├── clustervis.py
│   ├── flask_app.py
└── └── vis_development_app.py

DATA DIRECTORY

The 'data' directory contains all scripts used for gathering the data. This includes data related to our clustering algorithm and ranking system.

The 'data' directory contains the following structure:
	
	The 'amenities' directory contains code related to the data capture from foursquare API. This data was used for finding amenities.

	The 'cluster_model_output' directory contains the code used for the clustering pipeline.

	The 'etl_scripts' contains code relating to etl processes for amenities and census tracts data.

	The 'gaz' directory contains census data.

	The 'sample' directory contains a sample clustering output used for the development of the front end components.

	The 'shape_data' contains code relating to the shapes of census tracts.

Please refer to Diagram_2 below for more information about the structure of the 'data' directory (note that elements inside the directories are not displayed in the diagram). 

Diagram_2
├── data/
│   ├── amenities/
│   ├── cluster_model_output/
│   ├── etl_scripts/
│   ├── features/
│   ├── gaz/
│   ├── sample/
└── └── shape_data/

DOCS DIRECTORY

The 'docs' directory contains files relating to flow charts and diagrams that help depict the structure of the project.

Please refer to Diagram_3 below for more information about the structure of the 'docs' directory.    

Diagram_3
├── docs/
│   ├── Census Data Gathering and Prep.docx
│   ├── Census_Data_Cleanup_Process.vsdx
│   ├── RELO Process Flow Diagram.odg
│   ├── RELO Process Flow Diagram.pdf
│   ├── Visual Component.docx
└── └── amenity-data-capture-approach.docx


INSTALLATION
------------

1. Check to ensure you have docker installed. If it is not installed, please install it. Once installed, start docker.
2. Download the docker image by using the following link (note, it may take some time): https://drive.google.com/drive/folders/1fLpTlLICH0b0PzTqubKvYd0obrnpSyfj?usp=sharing


EXECUTION
----------------

Please follow the following steps to run the code:

1. Open a Powershell or Terminal window and navigate into the directory where the docker image was downloaded in the Installation section.
2. Run 'docker load -i relodemo.tar' (note, you may need to run as root/with sudo on linux/mac)
3. Run 'docker run -it -p 5000:5000 relodemo' (note, you may need to run as root/with sudo on linux/mac)
4. In your Powershell or Terminal window, once you see "Running on http://0.0.0.0:5000/", navigate to that link and begin using the app!

