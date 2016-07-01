#FIND COMMUNITIES IN NETWORKS

The purpose of this project is to apply some clustering algorithm to find communities in networks on a graph dataset which contains records of commercial flights information in the USA between 1987 and 2015.

The original dataset contains 160M records of flights that have been cleaned, aggregated by route and imported in Neo4j using Spark. You can find this part of the project [here](https://github.com/federico-fiorini/storage-systems-comparison).

Aggregating the flights we could detect the daily, monthly and yearly frequency of each route. This project is based on the yearly frequency which is used to weight the edges between the nodes. The result of this process of aggragation is in fact a weighted graph with the airports as nodes, the routes as edges and the yearly frequency as weight of the edge.

Starting from this weighted graph we could apply some clustering algorithms to detect communities in networks.

###THE ALGORITHMS

We decided to compare two opposite approches to the problem of finding communities in networks: an agglomerative approach and a divisive one. These are in fact the two broad classes of algorithms that focus on the addition or removal of edges to or from the network.

- Agglomerative algorithm: Random walks (Pascal Pons, Matthieu Latapy)
- Divisive algorithm: Shortest-path betwenness (M. E. J. Newman, M. Girvan)

###HOW TO SETUP & RUN

To run the algorithms you need to have a Neo4j database running and with already yearly aggregated data.

	# Have a neo4j instance of the database running on localhost

	# Run random walks
	python src/walktrap_visualization.py
	
	# Run shortest-path betwenness
	python src/girvan_newman.py
