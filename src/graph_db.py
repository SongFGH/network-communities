from py2neo import Graph, Node, Relationship
from py2neo.packages.httpstream import http

http.socket_timeout = 9999

def nodesAndEdges():
  graph = Graph()
  # Aggregate by year query
  # query= """
  # MATCH (a:Airport)-[d:DAILY_FLIGHTS]->(b:Airport)
  # WITH a, b, d.year AS year, sum(toInt(d.frequency)) AS yearly_freq
  # CREATE (a)-[m:YEARLY_FLIGHTS { year : year, frequency : yearly_freq }]->(b)
  # """
  
  year = "2015"
  # Get all routes for that year (edges)
  # Ignoring the direction retrieves a route twice
  query = """
    MATCH (a:Airport)-[n:YEARLY_FLIGHTS]-(b:Airport)
    WHERE n.year = '%s'
    RETURN a.code AS origin, n, b.code AS dest
    """ % year
  edges = graph.cypher.execute(query)

  # Get all active airports for that year (AIRPORTS) | TODO: is this the best way?
  query = """
    MATCH (a:Airport)-[n:YEARLY_FLIGHTS]-(b:Airport)
    WHERE n.year = '%s'
    RETURN a.code as id, count(*)
    """ % year
  nodes = graph.cypher.execute(query)

  return nodes, edges