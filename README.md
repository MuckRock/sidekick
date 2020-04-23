# Sidekick

Sidekick is a human-in-the-loop tool for document classification.

## Preprocessing

To begin, you need a large collection of `.txt` files. Then, preprocess the files by running:

```bash
cd preprocess
pipenv run preprocess.py
```

If this is your first time running, the word embedding models will also be auto-downloaded, which can take some time.

As a rough benchmark of running time, this code takes about 5 minutes to process 13k large and messy text docs, or about 2 minutes to process 130k relatively small and clean text docs. This script uses multiprocessing and is thus pretty CPU-intensive.

## Running the server

The backend is a minimal Flask app. There are provided Makefiles to quickly run the appropriate commands. From the top-level, run:

```bash
make server
```

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

The server will launch at `http://localhost:3000`.

The frontend assumes the backend is running on port 5000. You can change the server URL in the `frontend` directory by modifying `.env`.
