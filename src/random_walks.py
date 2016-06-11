#! /usr/bin/python

import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, is_valid_linkage
import numpy
from graph_db import nodesAndEdges
import pdb


def distance(vector1, vector2):
  diff = numpy.dot(degrees_neg_1_2,  vector1) - numpy.dot(degrees_neg_1_2,  vector2)
  return numpy.linalg.norm(diff) # distance between nodes


def delta(vector1, vector2, n):
  diff = distance(vector1, vector2)
  return ( 1.0/n ) * ( 1.0/2.0 ) * ( diff ** 2 )


def communityDelta(delta_matrix, communities, c1, c2, c):
  return (
    ( ( len(communities[c1]) + len(communities[c]) ) * delta_matrix[c1, c] )
  + ( ( len(communities[c2]) + len(communities[c]) ) * delta_matrix[c2, c] )
  - ( len(communities[c]) * delta_matrix[c1, c2] )
  ) / ( len(communities[c1]) + len(communities[c2]) + len(communities[c]) )


def mergeCommunities(k, j, communities, neighbours, delta_matrix, Z):
  # Create new community merging previous ones
  communities.append(communities[k] + communities[j])

  # Create new neighbours entry merging previous ones
  i = len(communities) - 1
  neighbours[i] = list(set(neighbours[k] + neighbours[j]))

  # print "(%d, %d) -> %d [%f]" % (k, j, i, delta_matrix[k,j])

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

  #Add step to linkage matrix
  Z.append( numpy.array([ k, j, delta_matrix[k,j], len(communities[i])], numpy.float64) )

  # Update delta matrix
  tmp_delta = delta_matrix
  delta_matrix = numpy.empty((i+1, i+1))
  delta_matrix[:-1, :-1] = tmp_delta

  # Update only adjacent communities' delta sigma
  for n in neighbours[i]:
    comm_delta = communityDelta(delta_matrix, communities, c1=k, c2=j, c=n)
    delta_matrix[n][i] = comm_delta
    delta_matrix[i][n] = comm_delta # TODO: check if we can remove this, I think is not needed

  return (communities, neighbours, delta_matrix, Z)


def modularity(communities, neighbours, original_neighbours, n_edges):
  m = []
  # The 'neighbours' dictionary keeps track of the current communities and their neighbours
  # while the 'communities' array keeps every community even after merging
  for community_id, neighbours_list in neighbours.iteritems(): 
    e_edges = 0 # internal edges of the community
    a_edges = 0 # any edge in the community
    c = communities[community_id]
    for v in c: # for every vertix in the community
      i_neighbours = filter(lambda x: x in c, original_neighbours[v]) #get only the neighbours inside the community
      e_edges = e_edges + len(i_neighbours)
      a_edges = a_edges + len(original_neighbours[v])

    e_edges = e_edges / 2 # We get duplicated inter edges because vertices inside a community are neighbours
    a_edges = a_edges - e_edges # Remove the duplicated edges also from the general edge count

    e_edges_fraction = e_edges / n_edges
    a_edges_fraction = a_edges / n_edges

    m.append(e_edges_fraction - pow(a_edges_fraction, 2))

  # print "modularity for partition"
  # print list(neighbours)
  # print sum(m)
  return sum(m)
  

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

# Get number of edges
i = 0
n_edges = 0
while i < (length-1):
  # Sum only the upper triangule of the A matrix
  # TODO: can we just measure the size of the edges return by the cypher query? how can we make sure we are not counting an edge twice? 
  n_edges = n_edges + sum(A[i+1][i+1:length])
  i = i + 1

n_edges = float(n_edges)

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
# numpy.savetxt("Pt.csv", Pt, fmt="%f", delimiter=",")

# Elevate the diagonal degrees matrix to the negative 1/2 power
degrees_neg_1_2 = numpy.zeros(degrees.shape)
numpy.fill_diagonal( degrees_neg_1_2, 1/(degrees.diagonal()**0.5) )

# Initiate delta matrix
delta_matrix = numpy.empty([length, length])
for i, neighbours_list in neighbours.iteritems():
  for j in neighbours_list:
    delta_matrix[i][j] = delta(Pt[i], Pt[j], n=length)
# numpy.savetxt("delta.csv", delta_matrix, fmt="%f", delimiter=",")

# List to keep track of the linkage matrix used for building the dendogram
Z = []

# Keep original neighbours to use in the Modularity calculation
original_neighbours = dict(neighbours)
# Q will keep the modularity value after each partition is made
Q = []
# community_at_step will keep the structure of the communities through every merging step
communities_at_step = []

#Get Starting Communities and Modularity
communities_at_step.append( list(neighbours.keys()) )
Q.append(modularity(communities, neighbours, original_neighbours, n_edges))

# Start merging communities
while len(neighbours) > 1:
  min_index = (None, None)
  min_value = None
  for i, l in neighbours.iteritems():
    for j in l:
      if min_value == None or delta_matrix[i][j] < min_value:
        min_value = delta_matrix[i][j]
        min_index = (i, j)

  (communities, neighbours, delta_matrix, Z) = mergeCommunities(min_index[0], min_index[1], communities, neighbours, delta_matrix, Z)
  communities_at_step.append( list(neighbours.keys()) )
  Q.append(modularity(communities, neighbours, original_neighbours, n_edges))

print Q
exit()
# Setup Dendogram
# plt.figure(figsize=(25, 100))
plt.title('Random Walks Dendrogram')
plt.xlabel('Communities')
plt.ylabel('delta Sigma')
dendrogram(
  numpy.asarray(Z),
  # p=10,
  # truncate_mode='lastp',
  # show_leaf_counts=False,
  leaf_rotation=90.,  # rotates the x axis labels
  leaf_font_size=6.,  # font size for the x axis labels
  # show_contracted=True,
  # orientation='bottom'
)
plt.show()