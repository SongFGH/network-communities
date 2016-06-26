import networkx
import sys
from graph_db import nodesAndEdges, get_max_frequency
import time
import matplotlib.pyplot as plt
import os

airports = {}


def root_dir():
    return os.path.abspath(os.path.dirname(__file__))


def get_communities(components):
        return [list(c) for c in components]


# Keep removing edges from Graph until one of the connected components of Graph splits into two
# compute the edge betweenness
def girvan_newman_step(G):

    init_component_number = networkx.number_connected_components(G)
    component_number = init_component_number

    while component_number <= init_component_number:
        bw = networkx.edge_betweenness_centrality(G, weight='frequency')    #edge betweenness for G

        #find the edge with max centrality
        max_ = max(bw.values())

        #find the edge with the highest centrality and remove all of them if there is more than one!
        for k, v in bw.iteritems():
            if float(v) == max_:
                G.remove_edge(k[0],k[1])    #remove the central edge

        component_number = networkx.number_connected_components(G)    #recalculate the no of components


# Compute the modularity of current split
def get_modularity(G, deg_, m_):

    new_A = networkx.adj_matrix(G, weight="frequency")

    new_deg = update_deg(new_A, G.nodes())

    # Let's compute the Q
    components = networkx.connected_components(G)    #list of components
    print 'No of communities in decomposed G: %d' % networkx.number_connected_components(G)

    Mod = 0  # Modularity of a given partitionning
    for c in components:
        EWC = 0    # Number of edges within a community
        RE = 0    # Number of random edges
        for u in c:
            EWC += new_deg[u]
            RE += deg_[u]        # Count the probability of a random edge
        Mod += (float(EWC) - float(RE * RE) / float(2 * m_))

    Mod = Mod / float(2 * m_)

    return Mod


def update_deg(A, nodes):
    deg_dict = {}

    n = len(nodes)  #len(A) ---> some ppl get issues when trying len() on sparse matrixes!
    B = A.sum(axis=1)
    for i in range(n):
        deg_dict[nodes[i]] = B[i, 0]

    return deg_dict


# Run GirvanNewman algorithm and find the best community split by maximizing modularity measure
def run_girvan_newman(G, orig_deg, m_):

    # Find the best split of the graph
    best_modularity = -110.0
    modularity = 0.0
    best_communities = []

    while True:
        girvan_newman_step(G)
        modularity = get_modularity(G, orig_deg, m_)
        print "Modularity of decomposed G: %f" % modularity

        if modularity > best_modularity:
            best_modularity = modularity
            best_components = networkx.connected_components(G)
            best_communities = get_communities(best_components)

            print "Components:", best_communities

        if G.number_of_edges() == 0:
            break

    if best_modularity > 0.0:
        print "Max modularity (Q): %f" % best_modularity
        # print "Graph communities:", best_communities
    else:
        print "Max modularity (Q): %f" % best_modularity

    return best_communities

def main(argv):

    # Get graph
    start_time = time.time()
    print "-- Get graph"
    nodes, edges = nodesAndEdges()

    # Get max frequency to normalize edges weight
    max_freq = get_max_frequency() + 1

    # Create graph
    G = networkx.Graph()
    G_original = networkx.Graph()

    for route in edges:
        # Add edge to graph
        G.add_edge(int(route.origin_id), int(route.dest_id), frequency=float(route.freq))
        G_original.add_edge(int(route.origin_id), int(route.dest_id), frequency=float(route.freq))

        # Add to airports dict
        airports[route.origin_id] = route.origin
        airports[route.dest_id] = route.dest

    n = G.number_of_nodes()    #|V|
    A = networkx.adj_matrix(G, weight="frequency")    #adjacenct matrix

    m_ = 0.0   # Weighted version for number of edges
    for i in range(0, n):
        for j in range(0, n):
            m_ += A[i,j]
    m_ = m_/2.0

    # Calculate the weighted degree for each node
    orig_deg = update_deg(A, G.nodes())

    # Run Newman alg
    best_communities = run_girvan_newman(G, orig_deg, m_)

    # Draw best partition
    pos = networkx.spring_layout(G_original)
    f = open('results/girvan_newman.txt', 'w')

    import random

    # nodes
    for c in best_communities:
        f.write(','.join([str(airports[a]) for a in c]) + "\n")

        color = "#%06x" % random.randint(0, 0xFFFFFF)

        networkx.draw_networkx_nodes(G_original, pos,
                                   nodelist=c,
                                   node_color=color,
                                   node_size=300,
                                   alpha=0.8)

    networkx.draw_networkx_edges(G_original, pos, width=1.0, alpha=0.5)

    plt.savefig('plot/girvan_newman.png')
    f.close()

    print("--- %s seconds" % "{0:.2f}".format(time.time() - start_time))

if __name__ == "__main__":
    sys.exit(main(sys.argv))