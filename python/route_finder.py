from pathlib import Path

import pandas as pd
import numpy as np

import networkx as nx
from scipy.spatial import cKDTree

class RouteFinder:
    def __init__(self, systems, max_jump):
        self.system_names = {i:n.upper() for i,n in enumerate(systems.index)}
        self.name_index = {v:k for k,v in self.system_names.items()}
        self.systems = systems.reset_index(drop=True)
        self.max_jump = max_jump
        self.network_graph = self.initalise_graph()

    def initalise_graph(self):
        G = nx.Graph()
        G.add_nodes_from(self.systems.items())
        tree = cKDTree(list(self.systems))
        dist = tree.sparse_distance_matrix(tree, max_distance=self.max_jump, output_type='ndarray')
        G.add_edges_from(dist[dist['v']!=0][['i','j']])
        return G

    def find_route(self, A, B):
        A,B = A.upper(), B.upper()
        
        if A not in self.name_index:
            raise ValueError(f""" {A} not in Systems """)
            
        if B not in self.name_index:
            raise ValueError(f""" {B} not in Systems """)
        
        a_index = self.name_index[A]
        b_index = self.name_index[B]
        try:
            path = nx.algorithms.shortest_paths.generic.shortest_path(
                self.network_graph, a_index, b_index
            )
        except nx.exception.NodeNotFound:
            return "Route not possible"
        return [self.system_names[x] for x in path]

def test_route_finder():
    test_systems_pkl = Path(__file__).absolute().parent.parent / "data/systems.pkl"
    systems = pd.read_pickle(test_systems_pkl)

    max_jump = 25

    A = "LP 128-9"
    B = "Nu"
    import time
    t_start = time.time()
    rf = RouteFinder(systems, max_jump)
    path = rf.find_route(A, B)
    print(path)
    print(f"Completed in {round(time.time() - t_start,2)}s")

if __name__ == "__main__":
    test_route_finder()

