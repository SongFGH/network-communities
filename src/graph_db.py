from py2neo import Graph, Node, Relationship
from py2neo.packages.httpstream import http
import config
import requests
import json
import re
from util import Tree


http.socket_timeout = 9999

neo4j_host = config.NEO4J_HOST.rstrip('/')

header = {
    "Content-type": "application/json"
}

graph = Graph()
# year = "2015"


def nodesAndEdges(year=2015):
    graph = Graph()
    # Aggregate by year query
    # query= """
    # MATCH (a:Airport)-[d:DAILY_FLIGHTS]->(b:Airport)
    # WITH a, b, d.year AS year, sum(toInt(d.frequency)) AS yearly_freq
    # CREATE (a)-[m:YEARLY_FLIGHTS { year : year, frequency : yearly_freq }]->(b)
    # """

    # Get all routes for that year (edges)
    # Ignoring the direction retrieves a route twice TODO: why is this correct?? (*) random_walks.py line 78
    query = """
    MATCH (a:Airport)-[n:YEARLY_FLIGHTS{ year: '%s'}]-(b:Airport)
    WHERE n.frequency > 52
    RETURN a.code AS origin, ID(a) as origin_id, n.frequency as freq, b.code AS dest, ID(b) as dest_id
    """ % year
    edges = graph.cypher.execute(query)

    # Get all active airports for that year (AIRPORTS) | TODO: is this the best way?
    query = """
        MATCH (a:Airport)-[n:YEARLY_FLIGHTS{ year: '%s'}]-()
        WHERE n.frequency > 52
        RETURN a.code as code, ID(a) as id, a.city as city, a.state as state, count(*)
    """ % year
    nodes = graph.cypher.execute(query)

    return nodes, edges


def get_max_frequency():
    graph = Graph()

    query = """
        MATCH ()-[n:YEARLY_FLIGHTS]-()
        RETURN max(n.frequency) as max_freq
    """

    result = graph.cypher.execute(query)
    return int(result[0].max_freq)


def get_edges(year):
    query = """
        MATCH (a:Airport)-[n:YEARLY_FLIGHTS{ year: '%s'}]-(b:Airport)
        RETURN a.code AS origin, ID(a) as origin_id, a.state as origin_state, a.city as origin_city,
        n.frequency as freq, b.code AS dest, ID(b) as dest_id, b.state as dest_state, b.city as dest_city
        """ % year
    return graph.cypher.execute(query)

