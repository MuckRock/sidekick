# Sidekick

Sidekick is a human-in-the-loop tool for document classification.

## Preprocessing

To begin, you need a large collection of `.txt` files (recommended to place in `data/collections/[collection_name]`). Make sure you have Python `>=3.7` installed along with `pipenv` (dependencies may take a while to install). You also need `rust` installed to compile the spellchecker. Then, preprocess the files by running:

```bash
cd preprocess
pipenv run python preprocess.py [text_file_directory] [model_name]
```

where `[text_file_directory]` is a directory that contains top-level `.txt` files you wish to process and `[model_name]` is a simple string identifier for your model (e.g. `fbi`).

If this is your first time running, the word embedding models will also be auto-downloaded, which can take some time.

As a rough benchmark of running time, this code takes about 5 minutes to process 13k large and messy text docs, or about 2 minutes to process 130k relatively small and clean text docs. It will take a lot longer on first invocation to install dependencies. This script uses multiprocessing and is in general pretty CPU-intensive.

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
