class Tree:

    def __init__(self, root):
        self.root = root
        self.neighbours = {}
        self.inverted_neighbours = {}

    def add(self, edge):

        # Init keys
        self.init_neighbours_key(edge[0])
        self.init_neighbours_key(edge[1])

        # Add to neighbours dicts
        self.add_to_neighbours(from_node=edge[0], to_node=edge[1])

    def init_neighbours_key(self, key):
        """
        Initiate key if not exists
        :param key:
        :return:
        """
        if key not in self.neighbours:
            self.neighbours[key] = []

        if key not in self.inverted_neighbours:
            self.inverted_neighbours[key] = []

    def add_to_neighbours(self, from_node, to_node):
        """
        Add value if doesn't exist
        :param from_node:
        :param to_node:
        :return:
        """
        # Add to regular neighbours
        if to_node not in self.neighbours[from_node]:
            self.neighbours[from_node].append(to_node)

        # Add to inverted neighbours
        if from_node not in self.inverted_neighbours[to_node]:
            self.inverted_neighbours[to_node].append(from_node)

    def get_leaves(self):
        return [k for k, n in self.neighbours.items() if len(n) == 0 and k != self.root]

    def get_parents(self, node, distance):
        return [n for n in self.inverted_neighbours[node] if distance[n] == (distance[node] - 1)]

    def get_children(self, node, distance):
        return [n for n in self.neighbours[node] if distance[n] == (distance[node] + 1)]
