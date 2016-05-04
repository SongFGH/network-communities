#! /usr/bin/python

import numpy
from py2neo import Graph, Node, Relationship
from py2neo.packages.httpstream import http

http.socket_timeout = 9999

def nodesAndEdges():
	graph = Graph()
	# Aggregate by year query
	# query= """
	#	MATCH (a:Airport)-[d:DAILY_FLIGHTS]->(b:Airport)
	#	WITH a, b, d.year AS year, sum(toInt(d.frequency)) AS yearly_freq
	#	CREATE (a)-[m:YEARLY_FLIGHTS { year : year, frequency : yearly_freq }]->(b)
	#	"""
	
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

def distance(vector1, vector2):
	diff = numpy.dot( numpy.linalg.matrix_power(degrees, -1/2),  vector1) - numpy.dot( numpy.linalg.matrix_power(degrees, -1/2),  vector2)

	return numpy.linalg.norm(diff) # distance between nodes

def delta(vector1, vector2, n):
	diff = distance(vector1, vector2)
	return ( 1/n ) * ( 1/2 ) * ( diff ** 2 )

def communityDelta(delta_matrix, communities, c1, c2, c):
	return ( 
	  ( ( len(communities[c1]) + len(communities[c]) ) * delta_matrix[c1, c] )
	+ ( ( len(communities[c2]) + len(communities[c]) ) * delta_matrix[c2, c] )
	- ( len(communities[c]) * delta_matrix[c1, c2] ) 
	) / ( len(communities[c1]) + len(communities[c2]) + len(communities[c]) )
	
def mergeCommunities(k, j, communities, neighbours, delta_matrix):
	# Create new community merging previous ones
	communities.append(communities[k] + communities[j])

	# Create new neighbours entry merging previous ones
	i = len(communities) - 1
	neighbours[i] = list(set(neighbours[k] + neighbours[j]))

	print "(%d, %d) -> %d" % (k, j, i)

	# Update neighbours of the new comunity removing previous communities that have been merged
	try:
		neighbours[i].remove(k)
	except ValueError:
		pass

	try:
		neighbours[i].remove(j)
	except ValueError:
		pass
	
	# For each neighbour, remove previous communities and add new one
	for n in neighbours[i]:
		try:
			neighbours[n].remove(k)
		except ValueError:
			pass

		try:
			neighbours[n].remove(j)
		except ValueError:
			pass
		
		neighbours[n].append(i)

	# Delete old communities' neighbours
	del neighbours[k]
	del neighbours[j]

	# Update delta matrix
	tmp_delta = delta_matrix
	delta_matrix = numpy.empty((i+1, i+1))
	delta_matrix[:-1, :-1] = tmp_delta

	# Update only adjacent communities' delta sigma
	for n in neighbours[i]:
		comm_delta = communityDelta(delta_matrix, communities, c1=k, c2=j, c=n)
		delta_matrix[n][i] = comm_delta
		delta_matrix[i][n] = comm_delta # TODO: check if we can remove this, I think is not needed

	return (communities, neighbours, delta_matrix)



nodes, edges = nodesAndEdges()
length = len(nodes)

# A: Initiate as identity matrix
A = numpy.identity(length)

i = 0
# Airports dictionary CODE: ID
airports = {}
# Airports neighbours dictionary
neighbours = {}
# Cluster communities
communities = []

# For each node, initiate dictionary, neighbours and communities
for airport in nodes:
	airports[airport.id] = i
	neighbours[i] = []
	
	communities.append([i])
	i = i + 1

# For each route:
for route in edges:
	origin_index = airports[route.origin]
	dest_index = airports[route.dest]

	# Populate A with connections between airports
	A[origin_index, dest_index] = 1 # TO-DO: change 1 with edge weight (frequency) ?
	# Populate neighbours tree
	neighbours[origin_index].append(dest_index)

#numpy.savetxt("A.csv", A, fmt="%i", delimiter=",")

# Calculate degree matrix
degrees = numpy.zeros([length, length])
for code, i in airports.iteritems():
	degree = numpy.sum(A[i])
	degrees[i][i] = degree
#numpy.savetxt("degrees.csv", degrees, fmt="%i", delimiter=",")

# Calculate P 
P = numpy.dot( numpy.linalg.matrix_power(degrees, -1) , A)

#numpy.savetxt("P.csv", P, fmt="%f", delimiter=",")

t = 3
Pt = P * t
#numpy.savetxt("Pt.csv", Pt, fmt="%f", delimiter=",")

# Initiate delta matrix
delta_matrix = numpy.empty([length, length])
for i, neighbours_list in neighbours.iteritems():
	for j in neighbours_list:
		delta_matrix[i][j] = delta(Pt[i], Pt[j], n=length)

#numpy.savetxt("dist.csv", dist, fmt="%f", delimiter=",")

# Start merging communities
while len(neighbours) > 1:
	min_index = (None, None)
	min_value = None
	for i, l in neighbours.iteritems():
		for j in l:
			if min_value == None or delta_matrix[i][j] < min_value:
				min_value = delta_matrix[i][j]
				min_index = (i, j)

	(communities, neighbours, delta_matrix) = mergeCommunities(min_index[0], min_index[1], communities, neighbours, delta_matrix)

# print communities
