

"""
Main module of the server file
"""

# 3rd party moudles
from flask import Flask, render_template
# app = Flask(__name__)


# local modules
import config


# Get the application instance
connex_app = config.connex_app

# Read the swagger.yml file to configure the endpoints
connex_app.add_api("swagger.yml")


# create a URL route in our application for "/"
@connex_app.route("/")
def home():
    """
    This function just responds to the browser URL
    0.0.0.0:80/
    :return: the rendered template "home.html"
    """
    return render_template("home.html")


# run the app
if __name__ == "__main__":
    connex_app.run(host="0.0.0.0", port=80)
