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
import itertools
from typing import Set, Tuple, Union
from core.models import TableNode
from core.handlers import ReplaceEnvHandler, ReplaceSkipHandler, ReplaceSkipPartHandler
from core.util import get_module_logger

sys.setrecursionlimit(1000000)
APP_NAME = 'analyzer'


def parse_argument():
    parser = argparse.ArgumentParser(
        description="Searches for SQL files in the specified directory and parses the table lineage."
    )
    parser.add_argument("--input_dir", "-i", required=True)
    parser.add_argument("--env_path", "-e", default=".env")
    parser.add_argument("--pickle_path", "-p", default="data_lineage.pkl")
    parser.add_argument("--detailed_analysis", "-d", action='store_true')
    return parser.parse_args()


def create_env(env_path):
    if env_path is None:
        return None
    env = Env()
    env.read_env(env_path, recurse=False)
    return env


if __name__ == "__main__":
    logger = get_module_logger(APP_NAME, store_file=True)
    logger.info(f"{APP_NAME} has started.")

    args = parse_argument()
    env = create_env(args.env_path)

    replace_handler_list = []
    rp_skip_handler_create = ReplaceSkipHandler('^CREATE')
    replace_handler_list.append(rp_skip_handler_create)

    all_node_dict = dict()
    sql_path_list = list()
    sql_path_list.extend(glob.glob(f"{args.input_dir}/**/*.sql"))

    for sql_path in sql_path_list:
        sql_content = None
        try:
            sql_path_elements = os.path.dirname(sql_path).split('/')
            attr_dict = {}
            if args.detailed_analysis:
                job_name = sql_path_elements[-1]
                file_url = sql_path.replace(args.input_dir, '')
                attr_dict = {'job_name': job_name, 'file_url': file_url}
            logger.info(f"analyzing ...  {sql_path}")
            with open(sql_path, 'r') as input_file:
                sql_content = input_file.read()
                for rp_handler in replace_handler_list:
                    sql_content = rp_handler.run(sql_content)
                    if sql_content == '':
                        # 空文字に置き換えられた場合は次のファイルへ
                        break

                lineage_result = LineageRunner(sql_content, verbose=True)
                # sqllineageのプライベート関数を利用
                lineage_result._stmt = [
                    s
                    for s in sqlparse.parse(
                        sqlparse.format(lineage_result._sql.strip(
                        ), lineage_result._encoding, strip_comments=True),
                        lineage_result._encoding,
                    )
                    if s.token_first(skip_cm=True)
                ]
                lineage_result._stmt_holders = [LineageAnalyzer().analyze(
                    stmt) for stmt in lineage_result._stmt]
                for holder in lineage_result._stmt_holders:
                    source_tables = holder.read
                    target_tables = holder.write
                    # target一覧を探索して対応するsourceをtree構造にまとめていく
                    for target_table in target_tables:
                        target_elements = str(target_table).split('.')
                        target_db_name = target_elements[0]
                        target_table_name = target_elements[1]
                        target_node = all_node_dict.get(target_table_name)
                        if target_node is None:
                            # 初めて登場したテーブルの場合はTableNodeを生成する
                            target_node = TableNode(
                                target_db_name, target_table_name, attr_dict)
                            all_node_dict[target_node.name] = target_node
                        for source_table in source_tables:
                            source_elements = str(source_table).split('.')
                            source_db_name = source_elements[0]
                            source_table_name = source_elements[1]
                            if target_node.exist_source(source_table_name) is False:
                                # sourceが配下に見つからなかった場合
                                source_node = all_node_dict.get(
                                    source_table_name)
                                if source_node is None:
                                    # 全てのTableNodeのリストにも存在しない場合
                                    source_node = TableNode(
                                        source_db_name, source_table_name, attr_dict)
                                    all_node_dict[source_table_name] = source_node
                                target_node.add_source(source_node)

                    # source一覧を探索して対応するtargetをtree構造にまとめていく
                    for source_table in source_tables:
                        source_elements = str(source_table).split('.')
                        source_db_name = source_elements[0]
                        source_table_name = source_elements[1]
                        source_node = all_node_dict.get(source_table_name)
                        if target_node is None:
                            # 初めて登場したテーブルの場合はTableNodeを生成する
                            source_node = TableNode(
                                source_db_name, source_table_name, attr_dict)
                            all_node_dict[source_node.name] = source_node
                        for target_table in target_tables:
                            target_elements = str(target_table).split('.')
                            target_db_name = target_elements[0]
                            target_table_name = target_elements[1]
                            if source_node.exist_target(target_table_name) is False:
                                # targetが配下に見つからなかった場合
                                target_node = all_node_dict.get(
                                    target_table_name)
                                if target_node is None:
                                    # 全てのTableNodeのリストにも存在しない場合
                                    target_node = TableNode(
                                        target_db_name, target_table_name, attr_dict)
                                    all_node_dict[target_table_name] = target_node
                                source_node.add_target(target_node)
        except Exception as ex:
            logger.error(f"sql_path={sql_path}")
            logger.error(ex)
            logger.error(f"sql_content:")
            logger.error(sql_content)
            # エラーの状況を出力して続行

    with open(args.pickle_path, 'wb') as analyzed_file:
        pickle.dump(obj=all_node_dict, file=analyzed_file, protocol=3)

    logger.info("finished.")
