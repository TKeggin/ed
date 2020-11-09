from pathlib import Path

import pandas as pd
import numpy as np
import networkx as nx
from scipy.spatial import cKDTree




class RouteFinder:
    def __init__(self, systems, max_jump):
        self.systems = systems
        self.lookup = {ii:x[0] for ii,x in enumerate(systems)}
        self.max_jump = max_jump
        self.G = self.initalise_graph()

    def initalise_graph(self):
        G = nx.Graph()
        G.add_nodes_from(self.systems)
        tree = cKDTree([s[1]["pos"] for s in self.systems])
        dist_matrix = tree.sparse_distance_matrix(
            tree, max_distance=self.max_jump, output_type="dict"
        )
        edges = [
            (self.lookup[k[0]], self.lookup[k[1]], {"dist":v}) 
            for k,v in dist_matrix.items()
        ]
        G.add_edges_from(edges)
        return G

    def find_route(self, A, B, return_distances=True):
        path = nx.algorithms.shortest_paths.generic.shortest_path(
            self.G, A, B, weight="dist"
        )
        if return_distances:
            path_edges = [self.G.edges[x,y] for x,y in zip(path[:-1], path[1:])]
            distances = [e["dist"] for e in path_edges]
            return path, distances
        else:
            return path

    def distances_from_route(self, path):
        path_edges = [self.G.edges[x,y] for x,y in zip(path[:-1], path[1:])]
        distances = [e["dist"] for e in path_edges]
        return distances


def test_route_finder():
    test_systems_pkl = Path(__file__).absolute().parent.parent / "test_ed/test_data/systems.pkl"

    s = pd.read_pickle(test_systems_pkl)
    systems = [(name,{"pos":pos}) for name, pos in s.iteritems()]

    max_jump = 18.

    A = "LP 128-9"
    B = "Nu"

    rf = RouteFinder(systems, max_jump)
    path, distances = rf.find_route(A, B)
    print(path)

    print(f"AS:\n{[f'{d:.3f}' for d in distances]} \n     sum: {sum(distances):.3f}")

    OPLpath = ['LP 128-9', 'G 85-12', 'Blest', 'LHS 1561', 'Arinack', 'Djandji',
    'Wodimui', 'Malannher', 'LTT 1509', 'Dongzi', 'CD-47 990', 'Aymifa',
    'Nu']

    OPLdistances = rf.distances_from_route(OPLpath)

    print(f"OPL:\n{[f'{d:.3f}' for d in OPLdistances]} \n     sum: {sum(OPLdistances):.3f}")

if __name__ == "__main__":
    test_route_finder()

