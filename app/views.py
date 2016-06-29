from flask import render_template, abort
from app import app
import pdb
import csv
import os


def root_dir():
    return os.path.abspath(os.path.dirname(__file__))


def get_communities(file_name):
    communities = []
    try:
        with open(os.path.join('results', '%s.txt' % file_name)) as f:
            lines = f.readlines()
            for community in lines:
                communities.append([a.replace('\n','') for a in community.split(',')])
    except IOError:
        return None

    return communities


@app.route("/map/<string:filename>")
def map(filename):

    communities = get_communities(filename)
    if communities is None:
        abort(404)

    airports_info = {}

    with open(os.path.join(root_dir(),'static', 'csv', 'global_airports.csv')) as f:
        reader = csv.DictReader(f)
        for row in reader:
            airports_info[row['iata_faa']] = {'lat': row['latitude'], 'lon': row['longitude']}

    communities_info = []
    not_found = []
    for c in communities:
        air = []
        for a in c:
            try:
                air.append({'code': a, 'lat': airports_info[a]['lat'], 'lon': airports_info[a]['lon']})
            except:
                not_found.append(a)
        communities_info.append(air)
    return render_template('map.html', title='Map', airports=communities_info)
