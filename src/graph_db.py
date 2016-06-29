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
    RETURN a.code AS origin, ID(a) as origin_id, n.frequency as freq, b.code AS dest, ID(b) as dest_id
    """ % year
    edges = graph.cypher.execute(query)

    # Get all active airports for that year (AIRPORTS) | TODO: is this the best way?
    query = """
        MATCH (a:Airport)-[n:YEARLY_FLIGHTS{ year: '%s'}]-()
        RETURN a.code as code, ID(a) as id, count(*)
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


def get_nodes_test():

    # Get all active airports for that year (AIRPORTS) | TODO: is this the best way?
    query = """
        MATCH (a:Test)-[n:GOES]-()
        WITH a.code as code, ID(a) as id, count(*) AS count
        ORDER by ID(a)
        RETURN code, id, count
        """
    return graph.cypher.execute(query)


def dijikstra(from_node, to_node):

    data = {
        "to" : "%s/db/data/node/%s" % (neo4j_host, to_node),
        "cost_property" : "frequency",
        "relationships" : {
            "type": "YEARLY_FLIGHTS"
        },
        "algorithm": "dijkstra"
    }

    node_url = "%s/db/data/node/%s/paths" % (neo4j_host, from_node)

    response = requests.post(node_url, data=json.dumps(data), headers=header)
    if response.status_code != 200:
        return []

    paths = []
    content = json.loads(response.content)
    try:
        for c in content:
            path = []
            nodes = c['nodes']
            for node in nodes:
                node_id = re.search("node/[0-9]*", node).group(0).split('/')[1]
                path.append(int(node_id))
            paths.append(path)

    except KeyError:
        print "Something wrong"

    return paths


def shortest_path_tree(root_id, nodes, neighbours):

    s1 = {root_id: 0}
    s2 = nodes[:]
    s2.remove(root_id)

    # Tree object
    tree = Tree(root_id)

    # While s2 is not empty
    while s2:

        length = []

        # For each element of s1
        for s, dist in s1.items():

            # Get neighbours in s2
            s2_neighbours = [n for n in neighbours[s] if n['id'] in s2]
            if not s2_neighbours:
                continue

            # Find the one with maximum frequency
            local_max = max(s2_neighbours, key=lambda x: x['freq'] + dist)

            # Set departing node and append to length list
            local_max['from'] = s
            length.append(local_max)

        # Find edge with max frequency among local max edges
        edge = max(length, key=lambda x: x['freq'])

        # Add to tree
        tree.add((edge['from'], edge['id']))

        # Move node to s2
        s1[edge['id']] = edge['freq'] + s1[edge['from']]
        s2.remove(edge['id'])

        # print s1

    #
    # # Calculate shortest path for each combination of nodes
    # for to_node in nodes:
    #
    #     # Skip self
    #     if root_id == to_node:
    #         continue
    #
    #     paths = dijikstra(root_id, to_node)
    #     for path in paths:
    #         for i in range(len(path) - 1):
    #             k = i + 1
    #             edge = (path[i], path[k])
    #             tree.add(edge)
    #



    return tree
