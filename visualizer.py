#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import csv
import os
import argparse
import sys
from environs import Env, EnvError
import re
import pickle
import sqlparse
from sqllineage.core import LineageAnalyzer
from sqllineage.runner import LineageRunner
from treelib import Node, Tree
import itertools
from typing import Set, Tuple, Union
from core.models import TableNode
from core.handlers import ReplaceEnvHandler, ReplaceSkipHandler, ReplaceSkipPartHandler
from core.util import get_module_logger

sys.setrecursionlimit(1000000)
APP_NAME = 'visualizer'


def parse_argument():
    parser = argparse.ArgumentParser(
        description="Displays the data lineage of the specified table."
    )
    parser.add_argument("--kind", "-k", required=True, choices=['target', 'source'])
    parser.add_argument("--table_name", "-t", required=True)
    parser.add_argument("--pickle_path", "-p", default="data_lineage.pkl")
    return parser.parse_args()

def search_node(node, nest_cnt, kind, done_list, tree, skip_keyword='T|X[1-9]'):
    if kind == 'source':
        for k, v in node.source_dict.items():
            if k in done_list:
                # 探索中に一度登場したテーブルはスキップする（循環参照対策）
                continue
        
            if re.match(skip_keyword, k.upper()):
                continue

            tree.create_node(k, f"{nest_cnt}:{k}", parent=f"{nest_cnt-1}:{node.name}")
            done_list.append(k)
            search_node(v, nest_cnt+1, kind, done_list, tree)
    elif kind == 'target':
        for k, v in node.target_dict.items():
            if k in done_list:
                # 探索中に一度登場したテーブルはスキップする（循環参照対策）
                continue
        
            if re.match(skip_keyword, k.upper()):
                continue

            tree.create_node(k, f"{nest_cnt}:{k}", parent=f"{nest_cnt-1}:{node.name}")
            done_list.append(k)
            search_node(v, nest_cnt+1, kind, done_list, tree)


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

        # kind=targetの場合
        # 指定されたテーブルのtargetとなるテーブルをリストする
        # from 指定されたテーブル insert targetとなるテーブル
        # kind=sourceの場合
        # 指定されたテーブルのsourceとなるテーブルをリストする
        # from sourceとなるテーブル insert 指定されたテーブル
        nest_cnt = 0
        done_list = [args.table_name]
        tree = Tree()
        tree.create_node(args.table_name, f"{nest_cnt}:{args.table_name}")
        search_node(root_node, nest_cnt+1, args.kind, done_list, tree)
        tree.show()
    
    logger.info("finished.")
