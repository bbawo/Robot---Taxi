from graph import Graph

my_graph = Graph('data.txt')

# A print of the graph details
print('Graph Details')
for vertex, node in my_graph.nodes.items():
    print("%d x=%.2f y=%.2f"%(node.vertex, node.x, node.y))
    print("\t", node.edges)
    
print "............................................"
# An Example of a Query of the edges and vectors
# to a vertex. In this example vertex is 36 which we know 4\
# has four edges from the graph
vertex = 36
edges = my_graph.get_edges(vertex)
vectors = my_graph.get_vectors(vertex)
print('\nVertices that form edges with', vertex, 'are:')
for vert, weight in edges.items():
    print('\t%d with weight %.2f'%(vert, weight))


print('\nVertices that form vectors with', vertex, 'are:')
for vert, w_theta in vectors.items():
    print('\t%d with weight %.2f at %.2f degrees '%(vert, w_theta[0], w_theta[1]))

print "............................................."
# An example to trace directions. You can read the get_diection() method
# of the graph class to see how it traces the routes from the shortest paths
# list of tuples. This is a trace from Vertex 1 back to 1. Used starting
# theta of 0 
print('\n...directions from 1 to 23')
my_graph.get_directions(1,23,0)
print "....................................................................."
# Now we remove the edge from 4 to 48 and see what the new trace is
# for a direction from 1  to 1
success = my_graph.remove_edge(4,48)
if not success:
    print('Error:, Edge Missing')
# Now get shortest patn from 1 to 1. It should get a new path 
# that does not include the path from 4 to 48
print('\n...directions from 1 to 1 after removing edge 4 to 48')
my_graph.get_directions(1,1,0)

print "....................................................................."
#Given a passenger pickup coordinates, find location and navigate 
my_graph.eval_line_equations(-5.4, 28.8)
v1, v2 = my_graph.pickup_drop_off_vertices()
print "Your passenger is located between vertex {} and vertex {} ".format(v1, v2)
print my_graph.get_equation()
