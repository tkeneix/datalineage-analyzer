#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mimetypes import init
import os
import argparse
import sys
import re
import pickle
from typing import Set, Tuple, Union
from core.models import TableNode
from core.util import get_module_logger
import dash
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import dash_cytoscape as cyto

sys.setrecursionlimit(1000000)
APP_NAME = 'dash_visualizer'


def parse_argument():
    parser = argparse.ArgumentParser(
        description="Start the server to graph the data lineage."
    )
    parser.add_argument("--pickle_path", "-p", default="data_lineage.pkl")
    return parser.parse_args()

def search_node(node, nest_cnt, kind, done_list, cy_nodes, cy_edges, skip_keyword='T|X[1-9]'):
    if kind == 'source':
        for k, v in node.source_dict.items():
            if k in done_list:
                # 探索中に一度登場したテーブルはスキップする（循環参照対策）
                continue
        
            if re.match(skip_keyword, k.upper()):
                continue

            node_data = {'data': {'id': f"{nest_cnt}:{k}", 'label': f"{nest_cnt}:{k}"}, 'classes': 'source'}
            edge_data = {'data': {'source': f"{nest_cnt}:{k}", 'target': f"{nest_cnt-1}:{node.name}"}}
            cy_nodes.append(node_data)
            cy_edges.append(edge_data)
            done_list.append(k)
            search_node(v, nest_cnt+1, kind, done_list, cy_nodes, cy_edges)
    elif kind == 'target':
        for k, v in node.target_dict.items():
            if k in done_list:
                # 探索中に一度登場したテーブルはスキップする（循環参照対策）
                continue
        
            if re.match(skip_keyword, k.upper()):
                continue

            node_data = {'data': {'id': f"{nest_cnt}:{k}", 'label': f"{nest_cnt}:{k}"}, 'classes': 'target'}
            edge_data = {'data': {'source': f"{nest_cnt-1}:{node.name}", 'target': f"{nest_cnt}:{k}"}}
            cy_nodes.append(node_data)
            cy_edges.append(edge_data)
            done_list.append(k)
            search_node(v, nest_cnt+1, kind, done_list, cy_nodes, cy_edges)

def get_all_node(pickle_path):
    with open(pickle_path, 'rb') as analyzed_file:
        all_node_dict = pickle.load(file=analyzed_file)
        return all_node_dict

# global section
logger = get_module_logger(APP_NAME, store_file=True)
app = dash.Dash(__name__)
app.title = 'Data Lineage Visualizer'
server = app.server

stylesheet = [
    # Group selectors
    {
        "selector": 'node',
        'style': {
            "opacity": 0.9,
            "label": "data(label)",
            "color": "#333333"
        }
    },
    {
        "selector": 'edge',
        "style": {
            "target-arrow-color": "#cccccc",
            "target-arrow-shape": "triangle",
            "line-color": "#cccccc",
            'arrow-scale': 1,
            'curve-style': 'bezier'
        }
    },
    # Classes selectors
    {
        'selector': '.source',
        'style': {
            'background-color': '#191970',
            'line-color': '#808080'
        }
    },
    {
        'selector': '.target',
        'style': {
            'background-color': '#87ceeb',
            'line-color': '#808080'
        }
    },
    {
        'selector': '.root',
        'style': {
            'background-color': '#4169e1',
            'line-color': '#808080',
            'shape': 'star-five'
        }
    }
]

args = parse_argument()

if os.path.isfile(args.pickle_path) is False:
    logger.error(f"The pickle file does not exist. Please run analyzer first. pickle_path={args.pickle_path}")
    sys.exit(-1)

all_node_dict = get_all_node(args.pickle_path)
all_node_keys = list(all_node_dict.keys())

app.layout = html.Div([
    dcc.Markdown('''
        ##### Data Lineage Visualizer
    '''),
    dcc.Dropdown(
        id='table_name_id',
        options=all_node_keys,
        placeholder='Please specify the table name.'
    ),
    html.Div(children=[
        cyto.Cytoscape(
            id='cytoscape',
            elements=[],
            style={
                'height': '85vh',
                'width': '100%'
            },
            layout={
                'name': 'cose'
            },
            stylesheet=stylesheet
        ),
    ]),
    html.Div([], id='redirect_url')
])


@app.callback(
    Output('cytoscape', 'elements'),
    [Input(component_id='table_name_id', component_property='value')]
)
def update_output_div(table_name):
    if all_node_dict.get(table_name) is None:
        return []
    else:
        nest_cnt = 0
        done_list = [table_name]
        cy_nodes = []
        cy_edges = []
        node_data = {'data': {'id': f"{nest_cnt}:{table_name}", 'label': f"{nest_cnt}:{table_name}"}, 'classes': 'root'}
        cy_nodes.append(node_data)

        search_node(all_node_dict[table_name], nest_cnt+1, 'target', done_list, cy_nodes, cy_edges)
        search_node(all_node_dict[table_name], nest_cnt+1, 'source', done_list, cy_nodes, cy_edges)
        
        return cy_edges + cy_nodes

# This is sample code and link.
@app.callback(
    Output("redirect_url", "children"),
    Input("cytoscape", "tapNodeData"),
)
def displayTapNodeDataLink(data):
    if data:
        url = f"https://eow.alc.co.jp/search?q={data['label'].split(':')[1]}"
        return html.A(url, href=url, target="_blank")


if __name__ == "__main__":
    logger.info(f"{APP_NAME} has started.")
    app.run_server(host='0.0.0.0', port=5000, debug=True)
