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

The structure of this package begins with with the 'app' directory. The app directory is used to store all code associated with the visual application for Relo. The 'static' directory contains images and stylesheets used in the application. The 'templates' directory contains the files used for building the front end UI. Finally, the clustervis.py, flask_app.py, and vis_development_app.py files are used to run python code related to this project. Please refer to Diagram_1 below for more information about the structure of the 'app' directory (note the images that are stored in the 'static' directory are not included in the diagram below). 

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
   




INSTALLATION
------------

1. Check to ensure you have docker installed. If it is not installed, please install it. Once installed, start docker.
2. Download the docker image by using the following link (note, it may take some time): https://gtvault.sharepoint.com/sites/DVAProjectTeam490/Shared%20Documents/Project%20Resources%20and%20Discussions/Docker%20Image%20Sample/relodemo.tar


EXECUTION
----------------

Please follow the following steps to run the code:

1. Open a Powershell or Terminal window and navigate into the directory where the docker image was downloaded in the Installation section.
2. Run 'docker load -i relodemo.tar' (note, you may need to run as root/with sudo on linux/mac)
3. Run 'docker run -it -p 5000:5000 relodemo' (note, you may need to run as root/with sudo on linux/mac)
4. In your Powershell or Terminal window, once you see "Running on http://0.0.0.0:5000/", navigate to that link and begin using the app!

