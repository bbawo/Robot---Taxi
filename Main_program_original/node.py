class Node:
    def __init__(self, vertex, x, y, edges):
        self.vertex = vertex
        self.x = x
        self.y = y
        self.edges = edges
        self.vectors = {}
        self.equations = {}
    
    def init_paths(self, vertices):
        self.min_path = {}
        self.paths = {}
        for vertex in vertices:
            self.min_path[vertex] = (float('inf'), None)
            self.paths[vertex] =[]

        self.min_path[self.vertex] = (0, self.vertex)
        self.paths[self.vertex].append((0, self.vertex))

    def relax(self, u, v, w):
        du, pu = self.min_path[u]
        dv, pu = self.min_path[v]
        if dv > (du + w):
            self.min_path[v] = (du+w, u)
    
        if du < float('inf'):
            dv_path = (du+w, u)
            if dv_path not in self.paths[v]:
                self.paths[v].append(dv_path)

    
        
        
    
