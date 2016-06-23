from graph_db import shortest_path_tree, nodesAndEdges
import time
from Queue import Queue
import sys


try:
  from pyspark import SparkContext, SparkConf

  print("Spark Modules Imported")

except ImportError as e:
    print("Error Importing", e)
    sys.exit(1)

# Initiate variables
neighbours = {}

# Get graph
first_start_time = time.time()
print "-- Querying Neo4j to get graph"
nodes, edges = nodesAndEdges()
print("--- %s seconds" % "{0:.2f}".format(time.time() - first_start_time))

# Initiate neighbours
for route in edges:
    neighbours.setdefault(route.origin_id, []).append({'id': route.dest_id, 'freq': route.freq})

# Get nodes id
nodes_id = [n.id for n in nodes]

collection = []
for s in nodes_id:
    collection.append({'root': s, 'nodes': nodes_id, 'neighbours': neighbours})

def execute(data):

    # Init variables
    s = data['root']
    nodes_id = data['nodes']
    neighbours = data['neighbours']
    distance = {}
    weight = {}
    edges_weight = {}

    # Get shortest paths tree
    start_time = time.time()
    print "\n- Node %s" % s
    print "-- Building shortest path tree"
    tree = shortest_path_tree(s, nodes_id, neighbours)
    print("--- %s seconds" % "{0:.2f}".format(time.time() - start_time))

    # Implement Girvan Newman algorithm
    start_time = time.time()
    print "-- Running Girvan-Newman"

    # Init
    for k in tree.neighbours.keys():
        distance[k] = None
        weight[k] = None

    distance[s] = 0
    weight[s] = 1
    queue = Queue()

    for i in tree.neighbours[s]:
        distance[i] = distance[s] + 1
        weight[i] = weight[s]
        queue.put(i)

    # FIRST PART: weight nodes
    while not queue.empty():
        # Get element from queue
        i = queue.get()

        # For each neighbours
        for j in tree.neighbours[i]:

            # Case a: first time we pass by j
            if distance[j] is None:
                distance[j] = distance[i] + 1
                weight[j] = weight[i]
                queue.put(j)

            # Case b: distance is greater by 1
            elif distance[j] == distance[i] + 1:
                weight[j] = weight[j] + weight[i]

            # Case c: distance is lower
            elif distance[j] < distance[i] + 1:
                pass

    # SECOND PART: weight edges

    # Get leaves
    leaves = tree.get_leaves()

    # Init edges weight starting from leaves
    for l in leaves:
        for i in tree.inverted_neighbours[l]:
            edges_weight.setdefault((i, l), 0)
            edges_weight[(i, l)] += float(weight[i]) / float(weight[l])

    # Init dict with distance as key and list of nodes as value.
    group_by_dist = {}
    for k, v in distance.iteritems():
        group_by_dist.setdefault(v, []).append(k)

    # For each level of distance
    for l in range(max(distance.values()), 0, -1):

        # For each node at distance 'l'
        for j in group_by_dist[l]:

            # For each neighbour going up (inverted): add to queue
            queue = Queue()
            map(queue.put, tree.inverted_neighbours[j])

            # Loop through queue
            while not queue.empty():

                i = queue.get()

                # If already calculated: skip to next
                if (i, j) in edges_weight:
                    continue

                # Calculate sum of weight of the edges below
                sum = 0
                skip = False

                # For each neighbour going down: sum the weight
                for n in tree.neighbours[j]:
                    try:
                        sum += edges_weight[(j, n)]
                    except KeyError:
                        # Edge not yet calculated. Add to bottom of the queue
                        queue.put(i)
                        skip = True
                        break

                # Skip to next edge
                if skip:
                    break

                # Calculate above edge weight
                edges_weight.setdefault((i, j), 0)
                edges_weight[(i, j)] += (weight[i] / weight[j]) * (1 + sum)

    print("--- %s seconds" % "{0:.2f}".format(time.time() - start_time))

    return edges_weight


# Init spark context
sc = SparkContext('local[*]')
rdd = sc.parallelize(collection)
e = rdd.flatMap(lambda row: execute(row))
print e.collect()

print("\n------ TOTAL: %s seconds ------" % "{0:.2f}".format(time.time() - first_start_time))
