#! /usr/bin/python

import sys
import matplotlib.pyplot as plt
from graph_db import nodesAndEdges
import numpy
import networkx as nx
import subprocess
import random
import pdb

if len(sys.argv) > 1:
  try:
    year = int(sys.argv[1])
  except ValueError:
      print "First argument must be a year between 1987 and 2015"
      exit()
else:
  year = 2015

nodes, edges = nodesAndEdges(year)
length = len(nodes)

# Airports dictionary CODE: ID
airports = {}

# A saves the weight of the edges
A = numpy.zeros((length,length))

i = 0
# Initiate dictionary for each airport and assign them ids
for airport in nodes:
  airports[airport.code] = i
  i = i + 1

# Create graph
G = nx.Graph()

for route in edges:
  origin_index = airports[route.origin]
  dest_index = airports[route.dest]
  # Populate A with connections between airports
  A[origin_index, dest_index] = route.freq

# Create the file that will be the input for the walktrap algorithm
f = open('flights.net','w')

i = 0
# Fill file and networkx simple graph
while i < (length):
  j = i + 1
  while j < (length):
    if A[i][j] > 0:
      f.write("%d %d %d\n" % (i,j, A[i][j]))
      G.add_edge(i, j, frequency=A[i][j])
    j = j + 1
  i = i + 1

f.close()

# run walktrap
pipe = subprocess.Popen(["../walktrap02/walktrap", "flights.net", "-d1", "-s", "-b"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout_data, stderr_data = pipe.communicate()

output_lines = stdout_data.splitlines()

# Get the best modularity
Q = float(output_lines[0])

# Get the rest of the output
communities = output_lines[1:(len(output_lines))]
# Split the nodes in every line
communities = [ nodes.split(" ") for nodes in communities ]
# to int
communities = map( lambda x: map( lambda y: int(y), x), communities)

# Create the file that will be the input for the walktrap algorithm
f = open('results/walktrap_%d.txt' % year,'w')

# pos = nx.spring_layout(G) # positions for all nodes
pos = nx.shell_layout(G, communities)

# nodes
for c in communities:
  # Draw nodes in the communities
  color = "#%06x" % random.randint(0, 0xFFFFFF)
  nx.draw_networkx_nodes(G,pos,
                        nodelist= c,
                        node_color=color,
                        node_size=100)

  # Write the community's airports in a file to visualize with google maps
  f.write(','.join([airports.keys()[airports.values().index(a)] for a in c]) + "\n")

f.close()

# Draw the network edges
nx.draw_networkx_edges(G,pos,
                       edgelist=G.edges(),
                       width=1,
                       alpha=0.5,
                       edge_color='black')

plt.axis('off')
plt.show()




