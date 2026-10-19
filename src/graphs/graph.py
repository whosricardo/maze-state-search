class Graph:
    def __init__(self):
        self.adjacency = {}

    def add_vertex(self, vertex):
        # if not already in adjacency dict
        # add it (prevents overwrite)
        if vertex not in self.adjacency:
            self.adjacency[vertex] = []

    def add_edge(self, source, destination, weight):
        self.add_vertex(source)
        self.add_vertex(destination)

        self.adjacency[source].append((destination, weight))

    def get_neighbors(self, vertex):
        return self.adjacency.get(vertex, [])
