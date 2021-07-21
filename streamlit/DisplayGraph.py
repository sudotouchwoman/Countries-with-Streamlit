'''
Implements wrapper over networkx and pyvis. inits Directed Graph from formatted data
and triples (see page/content/model.json)
pyvis creates JS-powered HTML file and saves it in the directory
'''
import streamlit as st
from pyvis.network import Network
import networkx as nx
import pandas as pd


class DisplayGraph:
    G:nx.DiGraph
    groups:int
    def __init__(self) -> None:
        self.G = nx.DiGraph()
        self.groups = 0


    def fill(self, NETWORK:dict, settings:dict):
        '''
        Fill nx DiGraph with values from formatted dict
        using several settings, such as:
            colormap    : [3 * layers] list of strings with hex colorcodes for edges
            threshold   : dict, containing MIN and MAX values to differ the edge colors according to their weights
            distance    : dict, containig ints measuring space between nodes (X) in same layer and between two layers (Y)
        '''
        COLORMAP = settings['COLORMAP']
        THRESH = settings['THRESHOLD']
        DISTANCE = settings['DISTANCE']
        self.groups = len(NETWORK["layers"])
        for j, layer in enumerate(NETWORK['layers']):
            neurons = [pos for pos in range(-len(layer['neurons']),len(layer['neurons']),2)]
            positions = { index : position for index, position in enumerate(neurons)}
            for i, neuron in enumerate(layer['neurons']):
                self.G.add_node(
                    neuron['id'],
                    color=layer['color'],
                    group=layer['group'],
                    size=layer['size'],
                    y=DISTANCE['Y']*positions[i],
                    x=DISTANCE['X']*layer['group'],
                    shape=layer['shape'],
                    label=' ',
                    name=neuron['name'],
                    #title=(layer['type']+':\t'+neuron['name']))
                    # uncomment to display layer title
                    title=(neuron['name']))
        triples = NETWORK['triples']
        for triple in triples:
            if triple['weight'] > THRESH['MAX']:
                colour = COLORMAP[self.G._node[triple['from']]['group']][2]
            elif triple['weight'] < THRESH['MIN']:
                colour = COLORMAP[self.G._node[triple['from']]['group']][0]
            else:
                colour = COLORMAP[self.G._node[triple['from']]['group']][1]
            self.G.add_edge(
                triple['from'],
                triple['to'],
                width=(0.5*abs(triple['weight'])),
                color=colour,
                title=triple['weight'])


    # create html for network with pyvis and save it
    @st.cache(persist=True, show_spinner=False)
    def get_pyvis(self, options:dict):
        '''
        Creates pyvis Network object from contents of DiGraph
        then sets layout options and writes html file with the graph into given path
        '''
        nt = Network(
                options['height'],
                options['width'],
                directed=bool(options['directed']))
        nt.from_nx(self.G)
        nt.set_options(options['jsblob'])
        nt.write_html(options['HTML'])


    def get_dataframes(self, columns:dict)->list:
        '''
        produce list of DataFrames, holding data about the model's layers
        each df has the following structure:
            from:   node-name
            weight: edge-weight
            to:     node-name
        returns:
            list of DataFrames
        '''
        rows = [[] for _ in range(self.groups)]
        for src, dst, info in (self.G.edges(data=True)):
            (rows[self.G._node[src]['group']]).append((
                                                    self.G._node[src]['name'],
                                                    info['title'],
                                                    self.G._node[dst]['name']))
        dataframes = [
            pd.DataFrame(rows[group],
            columns=columns[header]) for header, group in zip(columns['headers'], range(self.groups))]
        for frame in dataframes:
            frame.index += 1
        return dataframes

# i honestly tried to make sort of a filter,
# but with streamlit and (!) submit-style outfit it becomes such a mess
# def filter_frame(to_filter:pd.DataFrame, box_names:list)->pd.DataFrame:
#     df_filtered = to_filter.copy()
#     for idx, column in enumerate(to_filter.columns):
#         uniques = to_filter[column].unique()
#         choice = (st.sidebar.selectbox(box_names[idx], uniques))
#         df_filtered = df_filtered.loc[df_filtered[column].eq(choice)]
#     return df_filtered