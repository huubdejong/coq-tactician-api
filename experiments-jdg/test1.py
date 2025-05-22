from pathlib import Path
from pytact.data_reader import data_reader
import polars as pl
import networkx as nx
import matplotlib.pyplot as plt

dataset_path = Path("/home/chaos/TacticianDataTemp/TacticianDataTemp/v15-stdlib-coq8.11/dataset").resolve()

with data_reader(dataset_path) as data:
    for idx, (relative_path, dataset) in enumerate(data.items()):
        print("Module:", dataset.module_name)
        if len(dataset.lowlevel.graph.nodes) == 0:
            continue

        data_lowlevel = dataset.lowlevel
        graph = data_lowlevel.graph
        nodes = [n for n in graph.nodes]
        edges = [e for e in graph.edges]

        print("Number of nodes:", len(nodes))
        print("Number of edges:", len(edges))

        all_tactic_sequences = []

        for defn in dataset.definitions(spine_only=True):
            if defn.proof is not None:
                tactic_sequence = [step.tactic.base_text for step in defn.proof]
                ## breakpoint()
                all_tactic_sequences.append(tactic_sequence)
                print("Tactic Sequence:")
                print(tactic_sequence)
                G = nx.DiGraph()
                for seq in tactic_sequence:
                    for i in range(len(seq) - 1):
                        G.add_edge(seq[i], seq[i + 1])
                plt.figure(figsize=(12, 8))
                pos = nx.spring_layout(G, seed=42)
                nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue',font_size=10, font_weight='bold', arrowsize=20)
                plt.title("Tactic Sequence Graph")
                plt.tight_layout()
                plt.show()
        breakpoint()