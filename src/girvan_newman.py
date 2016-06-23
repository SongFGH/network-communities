import networkx
from graph_db import nodesAndEdges, get_max_frequency
import time


# def update_deg(A, nodes):
#     deg_dict = {}
#     n = len(nodes)  #len(A) ---> some ppl get issues when trying len() on sparse matrixes!
#     B = A.sum(axis = 1)
#     for i in range(n):
#         deg_dict[nodes[i]] = B[i, 0]
#     return deg_dict


# def get_modularity(G, deg_, m_):
#     New_A = networkx.adj_matrix(G)
#     New_deg = update_deg(New_A, G.nodes())
#
#     #Let's compute the Q
#     comps = networkx.connected_components(G)
#     print 'No of communities in decomposed G: %d' % networkx.number_connected_components(G)
#     Mod = 0    #Modularity of a given partitionning
#     for c in comps:
#         EWC = 0    #no of edges within a community
#         RE = 0    #no of random edges
#         for u in c:
#             EWC += New_deg[u]
#             RE += deg_[u]        #count the probability of a random edge
#         Mod += ( float(EWC) - float(RE*RE)/float(2*m_) )
#     Mod = Mod/float(2*m_)
#     print "Modularity: %f" % Mod
#     return Mod


def girvan_newman_step(graph):

    # Get number of connected components
    init_component_number = networkx.number_connected_components(graph)
    component_number = init_component_number

    while component_number <= init_component_number:

        # Get shortest-path betweenness
        betweenness = networkx.edge_betweenness_centrality(graph, weight='frequency')

        # Get maximum value of betweenness
        max_value = max(betweenness.values())

        # Remove all edges with max value
        for k, v in betweenness.items():
            if float(v) == max_value:
                print "----- Remove edge (%s, %s)" % (k[0], k[1])
                graph.remove_edge(k[0], k[1])

        component_number = networkx.number_connected_components(graph)

    return networkx.connected_components(G)


def get_communities(components):
    return [list(c) for c in components]


def main():

    # Get graph
    first_start_time = time.time()
    print "-- Get graph"
    nodes, edges = nodesAndEdges()

    # Get max frequency to normalize edges weight
    max_freq = get_max_frequency() + 1

    # Create graph
    graph = networkx.Graph()
    for route in edges:
        graph.add_edge(int(route.origin_id), int(route.dest_id), frequency=float(max_freq - route.freq))

    communities_steps = []

    print("--- %s seconds" % "{0:.2f}".format(time.time() - first_start_time))

    print "-- Running Girvan-Newman"
    start_time = time.time()

    # n = graph.number_of_nodes()
    # A = networkx.adj_matrix(graph)
    #
    # m = 0.0  # the weighted version for number of edges
    # for i in range(0, n):
    #     for j in range(0, n):
    #         m += A[i, j]
    # m /= 2.0
    #
    # best_q = 0.0
    # orig_deg = update_deg(A, graph.nodes())

    # Run Girvan Newman algorithm
    while True:

        components = girvan_newman_step(graph)
        communities_steps.append(get_communities(components))
        print "--- Split into %s connected components" % len(communities_steps[-1])

        # Q = get_modularity(G, orig_deg, m)

        # print "Modularity of decomposed G: %f" % Q

        # if Q > best_q:
        #     BestQ = Q
        #     Bestcomps = networkx.connected_components(G)  # Best Split
        #     print "Components:", Bestcomps

        # Break when all edges are removed
        if graph.number_of_edges() == 0:
            break

    # if best_q > 0.0:
    #     print "Max modularity (Q): %f" % best_q
    #     print "Graph communities:", Bestcomps
    # else:
    #     print "Max modularity (Q): %f" % best_q

    print("--- %s seconds" % "{0:.2f}".format(time.time() - start_time))

    print communities_steps

if __name__ == "__main__":
    main()