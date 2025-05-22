from pathlib import Path
from pytact.data_reader import data_reader
import polars as pl
import networkx as nx
import matplotlib.pyplot as plt

#python3 -i experiments-jdg/test.py

G = nx.Graph()
dataset_path = Path("/home/chaos/TacticianDataTemp/TacticianDataTemp/v15-stdlib-coq8.11/dataset").resolve()

with data_reader(dataset_path) as data:
    #x = [k for k in data.keys()]
    #breakpoint()
    # data is everything. # Data is a dictionary
    # data.items() iterates over all the files in the dataset dictionary.
    #The keys of the dictionary are python paths to .bin files (.bin is the extension cap'n proto)
    count = 0
    for idx, (relative_path,dataset) in enumerate(data.items()):
        # dataset is class https://coq-tactician.github.io/api/pytactician-pdoc/pytact/data_reader.html#data_reader
        if len(dataset.lowlevel.graph.nodes) == 0:
            continue
        # breakpoint()
        data_lowlevel = dataset.lowlevel
        graph = data_lowlevel.graph
        nodes = list(graph.nodes)
        node_index_to_label = {i: node.label for i, node in enumerate(nodes)}
        # Add all nodes once
        G.add_nodes_from(node_index_to_label.values())
        # Add edges once
        for source_idx, node in enumerate(nodes):
            start = node.children_index
            end = start + node.children_count
            for i in range(start, end):
                edge_target = graph.edges[i].target
                if edge_target.dep_index != 0:
                    continue
                target_idx = edge_target.node_index
                source_label = node.label
                target_label = node_index_to_label.get(target_idx)
                if target_label:
                    G.add_edge(source_label, target_label)
        print(f"Graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        # Visualize graph for this dataset file
        print(dataset.module_name)
        plt.figure(figsize=(10, 10))
        nx.draw(G, with_labels=True, node_size=100, font_size=8)
        plt.show()
        breakpoint()