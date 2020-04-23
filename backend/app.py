from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import re
import glob
import json

# Constants
MODELS_DIR = "../models"


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
    # TODO: clean up this code

    collection_name = request.args.get("collection")
    params = request.get_json()
    constraints = params["constraints"]
    positive_docs = params["positiveDocs"]

    import numpy as np

    doc_vector_obj = np.load(
        os.path.join(MODELS_DIR, collection_name, "doc_vectors.npz")
    )
    # Grab document vector matrix
    doc_vectors = doc_vector_obj.get(doc_vector_obj.files[0])

    from lego_metric_learner import batch_update
    from scipy import stats
    from scipy.spatial.distance import cosine

    dists = {}
    percentiles = {}
    percentile_dicts = {}

    import time

    start_time = time.monotonic()

    def p_time(msg):
        print(time.monotonic() - start_time)
        print(msg)
        print("\n")

    for tag in constraints.keys():

        p_time("updating constraints")
        sub_constraints = constraints[tag]

        if len(sub_constraints) != 0:
            A_updated = batch_update(doc_vectors, sub_constraints)

            p_time("choleskying")

            L = np.linalg.cholesky(A_updated)  # the lower tri matrix
            # use the new metric to calculate a mean doc vector (using only positive docs)

            p_time("calculating mean vec")
            positive_docs_idx = positive_docs[tag]
            tfidf_vecs_postive_docs = doc_vectors[positive_docs_idx]
            mean_vec = np.mean(np.dot(tfidf_vecs_postive_docs, L), axis=0)

            p_time("getting updated vecs")
            # compare all docs in the table builder to the mean vector
            # and return list in order of similarity
            updated_tfidf_vecs = np.dot(doc_vectors, L)
        else:
            # No constraints, go purely off positive docs
            positive_docs_idx = positive_docs[tag]
            tfidf_vecs_postive_docs = doc_vectors[positive_docs_idx]
            mean_vec = np.mean(tfidf_vecs_postive_docs, axis=0)
            updated_tfidf_vecs = doc_vectors

        p_time("getting doc dists")
        # Generate cutoff percentiles for documents for model
        doc_dists = np.nan_to_num(
            [cosine(arr, mean_vec) for arr in updated_tfidf_vecs], 1
        )
        p_time("getting doc percentiles")
        doc_percentiles = stats.rankdata(doc_dists, "average") / len(doc_dists)
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
