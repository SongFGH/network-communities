from flask import render_template
from app import app
from app import api


def get_airports():
    return ["JFK", "DFW"]


@app.route("/")
def map():

    airports = get_airports()
    list = [{'code': a} for a in airports]
    return render_template('map.html', title='Map', airports=list)
