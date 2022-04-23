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
import networkx as nx

sys.setrecursionlimit(1000000)
APP_NAME = 'graph_visualizer'


def parse_argument():
    parser = argparse.ArgumentParser(
        description="Output the data lineage of the specified table."
    )
    parser.add_argument("--table_name", "-t", required=True)
    parser.add_argument("--pickle_path", "-p", default="data_lineage.pkl")
    parser.add_argument("--graph_path", "-g", default="graph.html")
    return parser.parse_args()

def search_node(node, nest_cnt, total_node_cnt, kind, done_list, G, skip_keyword='T|X[1-9]'):
    node_cnt = total_node_cnt
    if kind == 'source':
        for k, v in node.source_dict.items():
            if k in done_list:
                # 探索中に一度登場したテーブルはスキップする（循環参照対策）
                continue
        
            if re.match(skip_keyword, k.upper()):
                continue

            node_cnt += 1
            G.add_node(f"{node_cnt}:{k}")
            G.nodes[f"{node_cnt}:{k}"]["color"] = 'BLUE'
            G.nodes[f"{node_cnt}:{k}"]["node_info"] = {
                "name": k,
                "node_cnt": node_cnt,
                "description": "",
            }
            G.add_edge(f"{node_cnt}:{k}", f"{total_node_cnt}:{node.name}")
            done_list.append(k)
            node_cnt = search_node(v, nest_cnt+1, node_cnt, kind, done_list, G)
    elif kind == 'target':
        for k, v in node.target_dict.items():
            if k in done_list:
                # 探索中に一度登場したテーブルはスキップする（循環参照対策）
                continue
        
            if re.match(skip_keyword, k.upper()):
                continue

            node_cnt += 1
            G.add_node(f"{node_cnt}:{k}")
            G.nodes[f"{node_cnt}:{k}"]["color"] = 'RED'
            G.nodes[f"{node_cnt}:{k}"]["node_info"] = {
                "name": k,
                "node_cnt": node_cnt,
                "description": "",
            }
            G.add_edge(f"{total_node_cnt}:{node.name}", f"{node_cnt}:{k}")
            done_list.append(k)
            node_cnt = search_node(v, nest_cnt+1, node_cnt, kind, done_list, G)

    return node_cnt

if __name__ == "__main__":
    logger = get_module_logger(APP_NAME, store_file=True)
    logger.info(f"{APP_NAME} has started.")

    args = parse_argument()

    if os.path.isfile(args.pickle_path) is False:
        logger.error(f"The pickle file does not exist. Please run analyzer first. pickle_path={args.pickle_path}")
        sys.exit(-1)

    with open(args.pickle_path, 'rb') as analyzed_file:
        all_node_dict = pickle.load(file=analyzed_file)
        root_node = all_node_dict.get(args.table_name)
        if root_node is None:
            logger.error(f"The specified table does not exist. table={args.table_name}")
            sys.exit(-2)

        nest_cnt = 0
        done_list = [args.table_name]
        total_node_cnt = 0
        G = nx.Graph()
        G.add_node(f"{total_node_cnt+1}:{args.table_name}")
        G.nodes[f"{total_node_cnt+1}:{args.table_name}"]["color"] = 'BLACK'
        G.nodes[f"{total_node_cnt+1}:{args.table_name}"]["node_info"] = {
            "name": args.table_name,
            "node_cnt": total_node_cnt+1,
            "description": "",
        }
        search_node(root_node, nest_cnt+1, total_node_cnt+1, 'target', done_list, G)
        search_node(root_node, nest_cnt+1, total_node_cnt+1, 'source', done_list, G)

        from pyvis.network import Network
        net = Network(notebook=True)
        net.from_nx(G)
        net.show(args.graph_path)

    logger.info("finished.")
