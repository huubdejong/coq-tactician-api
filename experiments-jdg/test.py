
from pathlib import Path
from pytact.data_reader import data_reader
import polars as pl
import numpy as np 
import networkx as nx
import matplotlib 
import matplotlib.pyplot as plt 
import json
from pathlib import Path
matplotlib.use('Agg')



dataset_path = Path("/home/kr1staps/coq-tactician-api/TacticianDataTemp/TacticianDataTemp/v15-stdlib-coq8.11/dataset").resolve()

data_sets = {}

with data_reader(dataset_path) as data:
    # breakpoint()
    # data is everything.
    # data.items() iterates over all the files in the dataset dictionary.
    counts = {}
    for idx, (relative_path,dataset) in enumerate(data.items()):
        # https://coq-tactician.github.io/api/pytactician-pdoc/pytact/data_reader.html
        # breakpoint()
        
        if len(dataset.lowlevel.graph.nodes) == 0:
            continue

        module_sequence = dataset.module_name.split(".")

        if len(module_sequence) == 0:
            raise ValueError("bad")
        
        if len(module_sequence) == 1:
            library = None 
            subpackage = None
            filename = module_sequence[0]

        if len(module_sequence) == 2:
            library = module_sequence[0]
            subpackage = None 
            filename = module_sequence[1]

        if len(module_sequence) >= 3:
            library = module_sequence[0]
            subpackage = ".".join(module_sequence[1:-1]) #Play with this could be -2 or something 
            filename = module_sequence[-1]

        """
        

        LTT = [x for x in dataset.definitions(across_files = True, spine_only = True)]
        #LTT_nodes = [x.node for x in LTT]
        LTT_edges = [(x.node, y[1]) for x in LTT for y in x.node.children]

        G = nx.Graph()
        #G.add_nodes_from(LTT_nodes)
        G.add_edges_from(LTT_edges)
        laplacian_spectrum = nx.laplacian_spectrum(G)

        #H = nx.DiGraph()
        #H.add_nodes_from(LTT_nodes)
        #H.add_edges_from(LTT_edges)
        #laplacian_spectrum = nx.laplacian_spectrum(H)
        """

        #data_lowlevel = dataset.lowlevel
        #graph = data_lowlevel.graph

        # Initializing names for the node and edge collections. 
        
        nodes = [x for x in dataset.definitions(across_files = True, spine_only = True)]
        edges = [(x.node, y[1]) for x in nodes for y in x.node.children]

        # initializing both undirected and directed versions. 
        DG = nx.DiGraph()

        DG.add_nodes_from(nodes)
        DG.add_edges_from(edges)
        G = DG.to_undirected()

        d_connected_components = [c for c in sorted(nx.weakly_connected_components(DG), key=len, reverse=True)]
        d_connected_subgraphs = [DG.subgraph(c).copy() for c in d_connected_components]
        # This saves the adjaceny matrices as arrays
        d_adjaceny_matrices = [(nx.adjacency_matrix(c)).toarray() for c in d_connected_subgraphs]

        #d_alg_con = [nx.algebraic_connectivity(c) for c in d_connected_subgraphs]
        # making a list where each entry is a list containing, in order the 
        # max in degree, max out degree, min in)degree, min out degree, avergae of both
        degree_stats = []
        for g in d_connected_subgraphs:
            in_degrees = []
            out_degrees = []
            for n in g.nodes():
                in_degrees.append(g.in_degree(n))
                out_degrees.append(g.out_degree(n))
            degree_stats.append([max(in_degrees), max(out_degrees), min(in_degrees), min(out_degrees), sum(in_degrees)/len(in_degrees), sum(out_degrees)/len(out_degrees)])

        connected_components = [c for c in sorted(nx.connected_components(G), key=len, reverse=True)]
        connected_subgraphs = [G.subgraph(c).copy() for c in connected_components]
        alg_con = [nx.algebraic_connectivity(c) for c in connected_subgraphs if c.number_of_nodes() > 1]

        # Stores mean, max and min algebraic connectivity in order
        stats_al_con = [sum(alg_con)/len(alg_con), max(alg_con), min(alg_con)]
        
        # This produces lists where each entry is a dictionary where the key is the node, and the value is the
        # centrality. 
        centrality = [nx.degree_centrality(g) for  g in connected_subgraphs]
        in_centrality = [nx.in_degree_centrality(g) for g in d_connected_subgraphs]
        out_centrality = [nx.out_degree_centrality(g) for g in d_connected_subgraphs]

        max_centralities = [max(x.values()) for x in centrality]

        # Makes a list of the directed harmonic centralities
        d_harmonic_centrality = [nx.harmonic_centrality(g) for g in d_connected_subgraphs]

        try : 
            data_sets[library][subpackage][filename] = {"nodes" : nodes, "edges" : edges}
        except KeyError as e: 
            try:
                data_sets[library][subpackage] = {}
            except KeyError as e2:
                try: 
                    data_sets[library] = {}
                except KeyError: 
                    raise ValueError("Terrible")
                
    
    
                
    #with Path("mygraphs.json").open("w") as jsonfile:
    #    json.dump(data_sets,jsonfile)
    

        # This is a function which takes in a nodes and returns a list of the nodes which are children. 
        #def children(n):
         #   return [nodes[edges[n.children_index+i].target.node_index] for i in range(n.children_count)]

        # Now we need to make a list of edges to be read and added as a NetworkX digraph.  
        # Before we do that, let's see how many children don't belong to this graph. 
        # To do this, we will create a list of "misfits". 
        
        breakpoint()

        # rsync --recursive --archive --progress --human-readable tactician@167.99.182.29:/home/tactician/TacticianDataTemp TacticianDataTemp
        # type(www) is the lowevel pytact.graph_api_capnpn_cython.Dataset_Reader class
        # it has the fields:
        # - data_version: the "version of the data in this dataset" 
        # - definitions: the numbers (indices) of all the definitions in this file
        # - dependencies: the list of the Pathlike strings that contain the dependencies of this file, qua capnp serializations.
        # - dynamic: it looks like it's a dump of the graph the representative ,and other bits of information as a struct.
        # - graph: a graph reader -- gonna have to break this down elsewhere...
        # - has_data_version: true when the data_version field is set (like the other has_ names, this is coming from the capnp description allowing some fields to be optional)
        # - has_dependencies: true when the dependencies field is set
        # - has_graph: true when the graph field is set
        # - has_module_name: true when the module_mame field is set
        # - module_name: the module name that the file resides in
        # - representative: int -- the official docs say that this is the entrypoint of the global context of of definitions available when this file is required by another.  If no 'super'-global definitions, then this is set to len(graph.nodes).  But it's not perfectly clear what that means.
        print(dir(data_lowlevel))
        print(type(data_lowlevel))

        all_depIndices = [edge.target.dep_index for edge in data_lowlevel.graph.edges]
        all_depIndices_df = pl.DataFrame(all_depIndices)

        all_nodeIndices = [edge.target.node_index for edge in data_lowlevel.graph.edges]
        all_nodeIndices_df = pl.DataFrame(all_nodeIndices)
        a = 0

        for node in data_lowlevel.graph.nodes:
            children = []
            a1 = node.children_index
            a2 = node.children_count
            for j in range(a2):
                childIndex = data_lowlevel.graph.edges[a1 + j].target.node_index
                children.append(data_lowlevel.graph.nodes[childIndex])
            print("Node number " + str(node.identity) + " with children " + str([c.identity for c in children]))
            #breakpoint()

        # may need to skip ssr or ssreflect ?
        
        for c in dataset.definitions(spine_only=True):
            if c.proof != None:
                for i in range(len(c.proof)):
                    #print(c.proof[i].tactic.base_text)
                    if c.proof[i].tactic.base_text in counts:
                        counts[c.proof[i].tactic.base_text] += 1
                    else:
                        counts.update({c.proof[i].tactic.base_text: 1})
                a = c
        #print(a)
        
        # breakpoint()

# breakpoint() pauses execution so you can poke at stuff
# dir(object) tells you everything you can call on the object
# Keys are python paths to .bin files, which are cap'n proto files.  

# depIndex and nodeIndex
# depIndex: 
#   - Indicates to which graph a node belongs. How this should be resolved is not specified here.  However, a value of zero always points to the 'current' graph.
#   - The graph contained in a file may reference nodes from the graph of other files. This field maps
#       + a `DepIndex` into the a file that contains that particular node.
#       + The first file in this list is always the current file. It is guaranteed that no cycles exist in
#       + the dependency relation between files induced by this field (except for the self-reference of the file).


# nodeIndex:
#   - The index into `Graph.nodes` where this (the current) node can be found.

# The ordering of dataset.lowlevel.dependencies is such that dataset.lowlevel.dependencies[0] is the pointer to the file implementing the capnp descriptoin of the current file's module_name: dataset.lowlevel.module_name


""" Notes to self (Kristaps):

Dont' forget this!
python3 -i experiments-jdg/test.py

After defining
nodes = [n for n in graph.nodes]
edges = [e for e in graph.edges]
we set n0 = nodes[0].  

Let 
a0 = n0.children_index
ci0 = n0.children_index
cc0 = n0.children_count

n0_children = [edges[ci0+i].target.node_index for i in range(cc0)]

ACTUALLY, what I want is something like this:
n0_children = [nodes[edges[ci0+i].target.node_index] for i in range(cc0)]

So now I need to try to combine all of these.  How do I add all the edges at once?  
Something to the affect of 
edges_to_add = []
edges_to_add = [(nodes[i], nodes[edges[(nodes[i].children_index)+j].target.node_index]) for i in range(len(nodes)) for j in range(nodes[i].children_count)]

I seem to get an error running this though.  I guess this is because some children do not live in the graph. 
So, I suppose I need to write code that checks if a node is in the graph. 
"""



"""
Anyways, I made this

LFT = [x for x in dataset.definitions(across_files = False, spine_only = True)]

and 

LFF = [x for x in dataset.definitions(across_files = False, spine_only = False)]

LTT = [x for x in dataset.definitions(across_files = True, spine_only = True)]

LTT_nodes = [x.node for x in LTT]

LTT_children = [[x for x in y.node.children] for y in LTT]

LTT_edges = [(x.node, y[1]) for x in LTT for y in x.node.children]

H = nx.DiGraph()
H.add_nodes_from(LTT_nodes)
H.add_edges_from(LTT_edges)

values = [x for x in (nx.pagerank(H, alpha = 0.85)).values()]
M = max(values)

maximal_nodes =  [x for x in (nx.pagerank(H, alpha = 0.85)).keys() if (nx.pagerank(H, alpha = 0.85)[x] == M )]

orders = [len(x) for x in connected_components]
stats = [np.mean(orders), np.median(orders)]

"""  