from flask import Flask, render_template, jsonify, send_from_directory, request
from flask_restful import Resource, Api, reqparse, abort
from flask_cors import CORS
import os
import re
import datetime
import logging
import pickle
import traceback

### global parameters
PICKLE_PATH = "data_lineage.pkl"
DEFAULT_TREE_LEVEL = 1

### global variables
app = Flask(
    __name__, static_folder="frontend/build/static", template_folder="frontend/build"
)
CORS(app)
api = Api(app)
logging.basicConfig(level=logging.ERROR)

all_node_dict = None

# function section


def get_all_node(pickle_path=PICKLE_PATH) -> dict:
    global all_node_dict
    if all_node_dict is None:
        with open(pickle_path, "rb") as analyzed_file:
            all_node_dict = pickle.load(file=analyzed_file)

    return all_node_dict


def search_node(
    node, nest_cnt, kind, params, done_list, cy_nodes, cy_edges, skip_keyword="T|X[1-9]"
):
    if kind == "source":
        for k, v in node.source_dict.items():
            if k in done_list:
                # 探索中に一度登場したテーブルはスキップする（循環参照対策）
                continue

            if re.match(skip_keyword, k.upper()):
                continue

            if nest_cnt <= params["source_level"]:
                node_data = {
                    "data": {
                        "id": f"{nest_cnt}:{k}",
                        "label": f"{nest_cnt}:{k}",
                        "classes": "source",
                    }
                }
                edge_data = {
                    "data": {
                        "id": f"{nest_cnt}:{k} - {nest_cnt-1}:{node.name}",
                        "label": f"{nest_cnt}:{k} - {nest_cnt-1}:{node.name}",
                        "source": f"{nest_cnt}:{k}",
                        "target": f"{nest_cnt-1}:{node.name}",
                    }
                }
                cy_nodes.append(node_data)
                cy_edges.append(edge_data)

            done_list.append(k)
            params["max_source_level"] = max(
                nest_cnt, params["max_source_level"])
            search_node(v, nest_cnt + 1, kind, params,
                        done_list, cy_nodes, cy_edges)

    elif kind == "target":
        for k, v in node.target_dict.items():
            if k in done_list:
                # 探索中に一度登場したテーブルはスキップする（循環参照対策）
                continue

            if re.match(skip_keyword, k.upper()):
                continue

            if nest_cnt <= params["target_level"]:
                node_data = {
                    "data": {
                        "id": f"{nest_cnt}:{k}",
                        "label": f"{nest_cnt}:{k}",
                        "classes": "target",
                    }
                }
                edge_data = {
                    "data": {
                        "id": f"{nest_cnt-1}:{node.name} - {nest_cnt}:{k}",
                        "label": f"{nest_cnt-1}:{node.name} - {nest_cnt}:{k}",
                        "source": f"{nest_cnt-1}:{node.name}",
                        "target": f"{nest_cnt}:{k}",
                    }
                }
                cy_nodes.append(node_data)
                cy_edges.append(edge_data)

            done_list.append(k)
            params["max_target_level"] = max(
                nest_cnt, params["max_target_level"])
            search_node(v, nest_cnt + 1, kind, params,
                        done_list, cy_nodes, cy_edges)


# routing section
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<string:file_name>")
def under_public(file_name):
    return send_from_directory(os.path.join(app.root_path, "frontend/build"), file_name)


class check_health(Resource):
    # curl -H "accept: application/json" -H "Content-Type: application/json" -d '{"comment": "Hello, World."}' -XGET http://localhost:5000/api/v1/healthcheck
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("comment", type=str, default="")
        super().__init__()

    def get(self):
        args = self.reqparse.parse_args()
        ret_json = {"status": True}
        ret_json["comment"] = args["comment"]
        return ret_json


class get_tablenodes(Resource):
    # curl -H "accept: application/json" -H "Content-Type: application/json" -d '{"table_name": "members"}' -XGET http://localhost:5000/api/v1/tablenodes
    def get(self):
        query_string = request.query_string
        table_name = request.args.get("table_name")
        target_level = int(request.args.get("target_level"))
        source_level = int(request.args.get("source_level"))

        all_node_dict = get_all_node()
        nest_cnt = 0
        cy_nodes = []
        cy_edges = []

        done_list = [table_name]
        node_data = {
            "data": {
                "id": f"{nest_cnt}:{table_name}",
                "label": f"{nest_cnt}:{table_name}",
                "name": table_name,
                "classes": "root",
            }
        }
        cy_nodes.append(node_data)

        params = {
            "max_target_level": 0,
            "max_source_level": 0,
            "target_level": target_level,
            "source_level": source_level,
        }

        search_node(
            all_node_dict[table_name],
            nest_cnt + 1,
            "target",
            params,
            done_list,
            cy_nodes,
            cy_edges,
        )
        search_node(
            all_node_dict[table_name],
            nest_cnt + 1,
            "source",
            params,
            done_list,
            cy_nodes,
            cy_edges,
        )

        if params["target_level"] > params["max_target_level"]:
            params["target_level"] = params["max_target_level"]
        if params["source_level"] > params["max_source_level"]:
            params["source_level"] = params["max_source_level"]

        return {"nodes": cy_edges + cy_nodes, "params": params}


class get_tables(Resource):
    # curl -H "accept: application/json" -H "Content-Type: application/json" -XGET http://localhost:5000/api/v1/tables
    def get(self):
        all_node_keys = list(get_all_node().keys())
        return {"tables": all_node_keys}


# main section
if __name__ == "__main__":
    api.add_resource(check_health, "/api/v1/healthcheck")
    api.add_resource(get_tablenodes, "/api/v1/tablenodes")
    api.add_resource(get_tables, "/api/v1/tables")
    app.run(host="0.0.0.0", port=5000, debug=True)
