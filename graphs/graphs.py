import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
G.add_node("a")
G.add_nodes_from(["b", "c"])

print(G.nodes())

G.add_edge(1, 2)
edge = ("d", "e")
G.add_edge(*edge)
edge = ("a", "b")
G.add_edge(*edge)

G.add_edges_from([("a", "c"), ("c", "d"), ("a", 1), (1, "d"), ("a", 2)])
print(G.edges())

nx.draw(G)
plt.savefig("../testdata/simple_path.png")
plt.show()

print(nx.shortest_path(G, "a", "e"))
print(G.degree("a"))

G = nx.path_graph(4)
print(G.nodes())
print(G.edges())
