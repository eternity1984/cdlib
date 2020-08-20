import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from cdlib import NodeClustering
from cdlib.utils import convert_graph_formats
from community import induced_graph

__all__ = ["plot_network_clusters", "plot_community_graph"]

# [r, b, g, c, m, y, k, 0.8, 0.2, 0.6, 0.4, 0.7, 0.3, 0.9, 0.1, 0.5]
COLOR = (
    (1, 0, 0),
    (0, 0, 1),
    (0, 0.5, 0),
    (0, 0.75, 0.75),
    (0.75, 0, 0.75),
    (0.75, 0.75, 0),
    (0, 0, 0),
    (0.8, 0.8, 0.8),
    (0.2, 0.2, 0.2),
    (0.6, 0.6, 0.6),
    (0.4, 0.4, 0.4),
    (0.7, 0.7, 0.7),
    (0.3, 0.3, 0.3),
    (0.9, 0.9, 0.9),
    (0.1, 0.1, 0.1),
    (0.5, 0.5, 0.5)
)


def plot_network_clusters(graph, partition, position=None, figsize=(8, 8), node_size=200, plot_overlaps=False,
                          plot_labels=False, cmap=None):
    """
    Plot a graph with node color coding for communities.

    :param graph: NetworkX/igraph graph
    :param partition: NodeClustering object
    :param position: A dictionary with nodes as keys and positions as values. Example: networkx.fruchterman_reingold_layout(G). By default, uses nx.spring_layout(g)
    :param figsize: the figure size; it is a pair of float, default (8, 8)
    :param node_size: int, default 200
    :param plot_overlaps: bool, default False. Flag to control if multiple algorithms memberships are plotted.
    :param plot_labels: bool, default False. Flag to control if node labels are plotted.
    :param cmap: str or Matplotlib colormap, Colormap(Matplotlib colormap) for mapping intensities of nodes. If set to None, original colormap is used.

    Example:

    >>> from cdlib import algorithms, viz
    >>> import networkx as nx
    >>> g = nx.karate_club_graph()
    >>> coms = algorithms.louvain(g)
    >>> pos = nx.spring_layout(g)
    >>> viz.plot_network_clusters(g, coms, pos)
    """                  
    if not isinstance(cmap, (type(None), str, matplotlib.colors.Colormap)):
        raise TypeError("The 'cmap' argument must be NoneType, str or matplotlib.colors.Colormap, "
                        "not %s." % (type(cmap).__name__))

    partition = partition.communities
    graph = convert_graph_formats(graph, nx.Graph)
    if position==None:
        position=nx.spring_layout(graph)

    n_communities = len(partition)
    if cmap is None:
        n_communities = min(n_communities, len(COLOR))
        cmap = matplotlib.colors.ListedColormap(COLOR[:n_communities])
    else:
        cmap = plt.cm.get_cmap(cmap, n_communities)
    _norm = matplotlib.colors.Normalize(vmin=0, vmax=n_communities-1)
    fontcolors = list(map(lambda rgb: ".15" if np.dot(rgb, [0.2126, 0.7152, 0.0722]) > .408 else "w",
                          [cmap(_norm(i))[:3] for i in range(n_communities)]))

    plt.figure(figsize=figsize)
    plt.axis('off')

    fig = nx.draw_networkx_nodes(graph, position, node_size=node_size, node_color='w')
    fig.set_edgecolor('k')
    nx.draw_networkx_edges(graph, position, alpha=.5)
    for i in range(n_communities):
        if len(partition[i]) > 0:
            if plot_overlaps:
                size = (n_communities - i) * node_size
            else:
                size = node_size
            fig = nx.draw_networkx_nodes(graph, position, node_size=size,
                                         nodelist=partition[i], node_color=[i] * len(partition[i]), 
                                         cmap=cmap, vmin=0, vmax=n_communities-1)
            fig.set_edgecolor('k')
    if plot_labels:
        for i in range(n_communities):
            if len(partition[i]) > 0:
                nx.draw_networkx_labels(graph, position, font_color=fontcolors[i],
                                        labels={node: str(node) for node in partition[i]})

    return fig


def plot_community_graph(graph, partition, figsize=(8, 8), node_size=200, plot_overlaps=False, plot_labels=False, cmap=None):
    """
        Plot a algorithms-graph with node color coding for communities.

        :param graph: NetworkX/igraph graph
        :param partition: NodeClustering object
        :param figsize: the figure size; it is a pair of float, default (8, 8)
        :param node_size: int, default 200
        :param plot_overlaps: bool, default False. Flag to control if multiple algorithms memberships are plotted.
        :param plot_labels: bool, default False. Flag to control if node labels are plotted.
        :param cmap: str or Matplotlib colormap, Colormap(Matplotlib colormap) for mapping intensities of nodes. If set to None, original colormap is used..

        Example:

        >>> from cdlib import algorithms, viz
        >>> import networkx as nx
        >>> g = nx.karate_club_graph()
        >>> coms = algorithms.louvain(g)
        >>> viz.plot_community_graph(g, coms)
        """

    cms = partition.communities

    node_to_com = {}
    for cid, com in enumerate(cms):
        for node in com:
            if node not in node_to_com:
                node_to_com[node] = cid
            else:
                # duplicating overlapped node
                alias = "%s_%s" % (node, cid)
                node_to_com[alias] = cid
                edges = [(alias, y) for y in graph.neighbors(node)]
                graph.add_edges_from(edges)

    # handling partial coverage
    s = nx.subgraph(graph, node_to_com.keys())

    # algorithms graph construction
    c_graph = induced_graph(node_to_com, s)
    node_cms = [[node] for node in c_graph.nodes()]

    return plot_network_clusters(c_graph, NodeClustering(node_cms, None, ""), nx.spring_layout(c_graph), figsize=figsize,
                                 node_size=node_size, plot_overlaps=plot_overlaps, plot_labels=plot_labels, cmap=cmap)



