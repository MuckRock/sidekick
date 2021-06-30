from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import re
import glob
import json
import numpy as np
from lego_metric_learner import lego_learn
import time


# Constants
MODELS_DIR = "/code/data/models"


def expand_collection(collection):
    config = os.path.join(MODELS_DIR, collection, "params.json")
    with open(config, "r") as f:
        params = json.load(f)
    return {"name": collection, "params": params}


collections = [
    expand_collection(collection)
    for collection in sorted(
        [
            name
            for name in os.listdir(MODELS_DIR)
            if os.path.isdir(os.path.join(MODELS_DIR, name))
        ]
    )
]
collection_params = {
    collection["name"]: collection["params"] for collection in collections
}

collection_doc_vectors = {}


def get_collection_doc_vectors(collection_name):
    if collection_name in collection_doc_vectors:
        return collection_doc_vectors[collection_name]

    doc_vector_obj = np.load(
        os.path.join(MODELS_DIR, collection_name, "doc_vectors.npz")
    )
    # Grab document vector matrix
    doc_vectors = doc_vector_obj.get(doc_vector_obj.files[0])
    collection_doc_vectors[collection_name] = doc_vectors
    return doc_vectors


app = Flask(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/list_collections", methods=["GET"])
def list_collections():
    return jsonify(collections)


# Read all the text files
def alpha_num_order(string):
    # Sort in natural order: https://stackoverflow.com/a/39885192
    return "".join(
        [
            format(int(x), "020d") if x.isdigit() else x
            for x in re.split(r"(\d+)", string)
        ]
    )


def read_fn(fn):
    # Read and return file contents
    with open(fn, "r") as f:
        return f.read()


DOC_EXTENSION = ".txt"


@app.route("/list_documents", methods=["GET"])
def list_documents():
    collection_name = request.args.get("collection")
    if collection_name not in collection_params:
        # TODO: better error
        return []

    params = collection_params[collection_name]
    text_dir = os.path.join(MODELS_DIR, collection_name, params["text_dir"])
    text_file_names = sorted(
        glob.glob(os.path.join(text_dir, f"*{DOC_EXTENSION}")), key=alpha_num_order
    )

    get_collection_doc_vectors(collection_name)

    return jsonify(
        [name[: -len(DOC_EXTENSION)].split("/")[-1] for name in text_file_names]
    )


@app.route("/get_document", methods=["GET"])
def get_document():
    collection_name = request.args.get("collection")
    doc_name = request.args.get("document")
    if collection_name not in collection_params:
        return jsonify(None)

    params = collection_params[collection_name]
    text_dir = os.path.join(MODELS_DIR, collection_name, params["text_dir"])
    text_file_name = os.path.join(text_dir, doc_name + DOC_EXTENSION)
    with open(text_file_name, "r") as f:
        return jsonify(f.read())


@app.route("/update_tags", methods=["POST"])
def update_tags():
    collection_name = request.args.get("collection")
    params = request.get_json()
    constraints = params["constraints"]
    positive_docs = params["positiveDocs"]

    dists = {}
    percentiles = {}
    percentile_dicts = {}
    doc_vectors = get_collection_doc_vectors(collection_name)

    start_time = time.monotonic()

    def p_time(msg):
        print(time.monotonic() - start_time)
        print(msg)
        print("\n")

    for tag in constraints.keys():
        p_time("running everything")
        doc_dists, doc_percentiles = lego_learn(
            doc_vectors,
            constraints[tag],
            positive_docs[tag],
        )
        percentile_dict = {k: v for k, v in enumerate(doc_percentiles)}
        dists[tag] = doc_dists.tolist()
        percentiles[tag] = [
            (i, percentile) for i, percentile in enumerate(doc_percentiles)
        ]
        percentile_dicts[tag] = percentile_dict

    p_time("done")
    return jsonify(
        {
            "dists": dists,
            "percentiles": percentiles,
            "percentileDicts": percentile_dicts,
        }
    )
