from math import pi, atan2
from node import Node
class Graph:
    # Initiazes the graph details, evaluates the paths and
    # the edge vectors when the graph is complete. Any change 
    # to the graph should update the paths, edges and 
    # the vectors to ensure proper functioning. The only method 
    # that does such in this class does the updates when done. See 
    # the remove_edge method.
    def __init__(self, file_name):
        self.nodes = {}
        with open(file_name, 'r') as fid:
            for line in fid:
                data = line.split()
                vertex = int(data[0])
                x, y = float(data[1]), float(data[2])
                edges={}
                for index in range(3, len(data), 2):
                    edges[int(data[index])] = float(data[index+1]) 

                self.nodes[vertex] = Node(vertex, x, y,edges)
        
        self.eval_edge_vectors()
        self.evaluate_paths()

    # Calculate the edge vectors at each vertex. This is used assuming 
    # the path between two vertices runs through a straight line. It helps
    # in getting the angle to turn to as you reach each vertex of the graph
    def eval_edge_vectors(self):
        for vertex, node in self.nodes.items():
            for v, w in node.edges.items():
                xv, yv = self.nodes[v].x, self.nodes[v].y
                uvx = xv - node.x
                uvy = yv - node.y 
                theta = (180.0/pi) * atan2(uvy, uvx)
                node.vectors[v] = (w,theta)  

    # Uses Bellman-Ford Algorithm to get single source shortest
    # path to all vertices for each vertex of the graph. This function 
    def evaluate_paths(self):
        vertices = self.nodes.keys()
        for vertex, node in self.nodes.items():
            #Init Paths
            node.init_paths(vertices)

            #Pseudo Belman-Ford Single Source Shortest Path Algorithm
            for count in range(len(vertices)):
                for vertex in vertices:
                    for edge_vertex, edge_weight in self.nodes[vertex].edges.items():
                        #edge_vertex, edge_weight = edge
                        node.relax(vertex, edge_vertex, edge_weight)
            
            self.elim_zero_cycle(node)
            
    #Eliminate zero-cycle paths
    def elim_zero_cycle(self, node):
        cycle_paths = node.paths[node.vertex]
        min_path = node.min_path[node.vertex]
        min_distance, min_parent = float('inf'), node.vertex
        for path in cycle_paths:
            distance, parent = path
            if parent == node.vertex:
                continue
            if min_distance > distance:
                min_distance = distance
                min_parent = parent

        node.min_path[node.vertex] = (min_distance, min_parent)    

    # It does a recursive run through the dictionary formed from
    # the single shortest paths to trace routes from a source vertex 
    # to a destination vertex
    def shortest_path(self, source_vertex, dest_vertex):
        path = []
        curr_vertex = dest_vertex
        min_distance, parent = self.nodes[source_vertex].min_path[curr_vertex]
        #print(min_distance, parent)
        if min_distance == float('inf'):
            return min_distance, path
        weight, theta = self.nodes[parent].vectors[curr_vertex]
        path.append((curr_vertex, weight, theta))
        #print(path)
        curr_vertex = parent
        while(curr_vertex != source_vertex):
            distance, parent = self.nodes[source_vertex].min_path[curr_vertex]
            weight, theta = self.nodes[parent].vectors[curr_vertex]
            path.append((curr_vertex, weight, theta))
            curr_vertex = parent
        #print(path)
        path.reverse()
        return min_distance, path
    
    # removes an edge, updates info and evaluate new paths
    def remove_edge(self, u, v):
        if v in self.nodes[u].edges and v in self.nodes[u].vectors:
            #print('Here')
            del self.nodes[u].edges[v]
            del self.nodes[u].vectors[v]
            self.evaluate_paths()
            return True
        else:
            return False

    # Returns a dictionary of vertices as keys and weight as values
    # that form an edge to the vertex being queried. Use this to check 
    # that edges reported from graph are real
    def get_edges(self, vertex):
        return self.nodes[vertex].edges

    # Returns a dictionary of vertices as keys and a tuple (weight, theta)
    # as values for every edge to the vertex being queried. The angle i.e 
    # theta is referenced from the x-axis. Use this to confirm validity of 
    # the edge vectors reported as compared to approximated measured values.  
    def get_vectors(self, vertex):
        return self.nodes[vertex].vectors

    # Changes the shortest path to directions for guidance. Defaults to 
    # a current angular direction of 0 degrees.It prints the directions
    # for a journey from source to destination vertex
    def get_directions(self, source_vertex, dest_vertex, curr_theta = 0):   
        distance, path = self.shortest_path(source_vertex, dest_vertex)
        curr_vertex = source_vertex
        navigation_list = []
        print('...total distance =', distance)
        for p in path:
            next_vertex, weight, next_theta = p
            theta = next_theta - curr_theta
            if theta < -180:
                theta = theta + 360
            elif theta > 180:
                theta = 360 - theta
            #print(p)
            navigation_list.append([next_vertex, theta, weight])
            #print('At vertex %d, turn %.2f degrees and travel %.2f m to vertex %d'\
            #  %(curr_vertex, theta, weight , next_vertex))
            curr_vertex = next_vertex
            curr_theta = next_theta
        return navigation_list

    def eval_line_equations(self, xc, yc):
        for vertex, node in self.nodes.items():
            for v, w in node.edges.items():
                xv, yv = self.nodes[v].x, self.nodes[v].y
                uvx = xv - node.x
                uvy = yv - node.y 
                node.equations[v] = (yc- node.y - xc*(uvy/uvx) + node.x*(uvy/uvx))

    def pickup_drop_off_vertices(self):
        xxy = 10000.00
        for vtx, nde in self.nodes.items():
            for eq in nde.equations.values():
                if(abs(eq) < xxy):
                    xxy =abs(eq)
                    v1 = vtx
                    v2 = nde.equations.keys()[nde.equations.values().index(eq)]
                else:
                    pass

        return (v1, v2)

    ## Optional usage ....just for confirmation
    def get_equation(self, vertex1, vertex2):
        return self.nodes[vertex1].equations[vertex2]