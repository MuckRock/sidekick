# Sidekick

Sidekick is a human-in-the-loop tool for document classification.

## Getting started

To run Sidekick, you will need to first install [Docker](https://docs.docker.com/get-docker/), technology for running applications cross-platform. You will also need some familiarity with the command line.

Sidekick operates on collections of `.txt` text files corresponding to a document collection. To get started, prepare a collection of text files and place them in the subdirectory `data/collections/[collection_name]` (where `[collection_name]` is the name of your collection).

If you want to try out Sidekick without supplying a collection yourself, you can try using one of the sample collections in the `data/collections` directory (TK).

## Preprocessing

Run the following command in the terminal (from the root directory of this repository), where

- `[collection_name]` is the name of your document collection or one of the sample document collections (basically the name of a subdirectory in the `data/collections` directory)
- `[LANG]` is the language code of your document collection (`en` is English). These language codes are necessary to use the proper word embedding model — the full list of language models/codes can be found here: https://fasttext.cc/docs/en/crawl-vectors.html#models (look at the download URL of the language models to get the language code, where the URL is structured like `.../cc.[LANG].bin...`).

```bash
docker compose run -v ./data:/data -e document_directory=[collection_name] -e language=[LANG] --rm preprocess
```

As a rough benchmark of running time, this code takes about 5 minutes to process 13k large and messy text docs, or about 2 minutes to process 130k relatively small and clean text docs. It will take a lot longer on first invocation to install dependencies and download the language models. This script uses multiprocessing and is in general pretty CPU-intensive.

## Running the server

The backend is a minimal Flask app. There are provided Makefiles to quickly run the appropriate commands. From the top-level, run:

```bash
make server
```

The server will launch at `localhost:5000` with auto-reload, but it is an API server only. Run the frontend following the steps below to access the UI.

## Running the frontend

First, make sure the frontend dependencies are installed. You will have to have Node installed.

```bash
cd frontend
npm install
```

Then, from the top-level, you can use the provided Makefile to run the frontend server:

```bash
make web
```

The auto-reloading server will launch at `http://localhost:3000`.

The frontend assumes the backend is running on port 5000. You can change the server URL in the `frontend` directory by modifying `.env`.

### Commands

docker compose build preprocess && docker compose run -v ./preprocess/symspell:/symspell -e DOC_DIR=symspell --rm preprocess
