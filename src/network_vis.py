import networkx as nx
import plotly
import plotly.graph_objs as go
import random
import re

def get_unique_fun_from_dict(fun_dict):
    all_funs = set()
    for key in fun_dict.keys():
        all_funs.add(key)
    for fun_list in fun_dict.values():
        [all_funs.add(fun) for fun in fun_list]
    return all_funs

def get_digraph_from_dict(fun_dict):
    g = nx.DiGraph()

    #Add all nodes
    all_funs_with_classes = get_unique_fun_from_dict(fun_dict)
    for fun in all_funs_with_classes:
        maybe_class = re.match(r'(\w+\.)', fun) #None if no class
        if maybe_class:
            maybe_class = maybe_class.group(0) #Change SRE_Match into string
        g.add_node(fun, fun_class=maybe_class, x=0, y=0)

    #Cluster nodes by class
    unique_classes = {}
    for node in g.nodes():
        node_class = g.node[node]['fun_class']
        if node_class not in unique_classes:
            unique_classes[node_class] = (random.uniform(0, 1), random.uniform(0, 1)) #cluster centre (x,y)
    
    sigma = 0.15
    for node in g.nodes():
        node_class = g.node[node]['fun_class']
        class_x, class_y = unique_classes[node_class]
        g.node[node]['x'] = random.gauss(class_x, sigma)
        g.node[node]['y'] = random.gauss(class_y, sigma)
        
     
    #Add edges
    for key in fun_dict.keys():
        for called_fun in fun_dict[key]:
            g.add_edge(key, called_fun)
    return g

def plot_digraph(g):

    #Add nodes as a scatter trace
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            colorscale='Rainbow',
            color=[],
            size=[],
            line=dict(width=2)
        ),
    )

    page_ranks = nx.pagerank(g)
    unique_classes = []

    for node in g.nodes():
        x = g.node[node]['x']
        y = g.node[node]['y']
        node_name = node
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([node_name])
        node_trace['marker']['size'] += tuple([page_ranks[node]*1000])

        #Set node colour based on class
        node_class = g.node[node]['fun_class']
        if node_class not in unique_classes:
            unique_classes.append(node_class)
        node_class_as_nr = unique_classes.index(node_class)
        node_trace['marker']['color'] += tuple([node_class_as_nr])

    #Add edges
    edge_dict_list = []
    for edge in g.edges():
        x0 = g.node[edge[0]]['x']
        y0 = g.node[edge[0]]['y']
        x1 = g.node[edge[1]]['x']
        y1 = g.node[edge[1]]['y']
        edge_dict_list.append(dict(ax=x0, ay=y0, axref='x', ayref='y',
                x=x1, y=y1, xref='x', yref='y'))

    fig = go.Figure(data=[node_trace],
             layout=go.Layout(
                title='<br>Digraph of function calls',
                titlefont=dict(size=14),
                hovermode='closest',
                showlegend=False,
                margin=dict(b=25,l=10,r=10,t=45),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                annotations = edge_dict_list
             )
    )

    plotly.offline.plot(fig, filename='networkx')

