# Sidekick

Sidekick is a human-in-the-loop tool for document classification.

## Getting started

Running Sidekick is best achieved using Docker and Docker Compose.

### Installation steps

- Install [Docker](https://docs.docker.com/get-docker/), a platform for running software on any operating system
- Install [Docker Compose](https://docs.docker.com/compose/install/) (unnecessary on Windows and Mac since it comes with the Docker install on those platforms)
- Install the frontend web application by running the following command in your terminal (in the root directory of this repository):
  ```bash
  docker compose -f build.yml run --rm frontend_build
  ```

### Document collections

Sidekick operates on collections of `.txt` text files corresponding to a document collection.

To get started, prepare a collection of text files and place them in the subdirectory `data/collections/[collection_name]` (where `[collection_name]` is the name of your collection).

If you want to try out Sidekick without supplying a collection yourself, you can try using one of the sample collections in the `data/collections/amazon_instrument_reviews` directory (a collection of reviews for instruments on Amazon).

## Preprocessing

Before Sidekick can be used for a given document collection, the collection must be preprocessed. This step only has to run once per document collection, generally taking between 2 and 15 minutes, depending on the size of the collection and if this is the first time running (in which case additional downloads will occur behind-the-scenes). By frontloading the hard work, Sidekick can be used at interactive speeds for document analysis later on.

To preprocess a document collection, you must pass two parameters:

- `collection`: the folder in which the collection is stored (i.e. `data/collections/[collection_name]` above). This also serves as the name of the collection
- `language`: the two-letter language code of your document collection (`en` is English). These language codes are necessary to use the proper word embedding model — the full list of language models/codes can be found here: https://fasttext.cc/docs/en/crawl-vectors.html#models (look at the download URL of the language models to get the language code, where the URL is structured like `.../cc.[LANG].bin...`).

Open a terminal and run the following command, substituting `[collection]` and `[language]` with the appropriate parameters from above:

```bash
collection=[collection] language=[language] docker compose -f build.yml run --rm preprocess
```

### Demo collection

If you want to use the demo collection before you try your own data, try running the command above with `collection` set to `amazon_instrument_reviews` and `language` set to `en`:

```bash
collection=amazon_instrument_reviews language=en docker compose -f build.yml run --rm preprocess
```

### How long preprocessing takes

As a rough benchmark of running time, this code takes about 5 minutes to process 13k large and messy text docs, or about 2 minutes to process 130k relatively small and clean text docs. It will take a lot longer on first invocation to install dependencies and download the language models. This script uses multiprocessing and is in general pretty CPU-intensive.

### Troubleshooting

The preprocessing script is generally pretty compute-intensive and can require a few GB of disk space and up to 10 GB of RAM.

On some operating systems, like Mac OS, you may find the preprocessing command fails with a disk space error or a cryptic `Killed` message. If this is the case, you need to increase the disk space (in the former case) or the RAM (in the latter case) available to Docker. This [documentation guide](https://docs.docker.com/docker-for-mac/#resources) covers how to do this on Docker Desktop (applicable to Mac, specifically, but the steps are probably similar for Windows).

## Running the web application

The web application consists of a backend API server and a web frontend application. You can run both at once by simply issuing the command:

```bash
docker compose up
```

After half a minute or so, the servers should both be launched. You can then access the frontend web application by visiting [localhost:3000](http://localhost:3000) in your web browser.

If the application fails to load, make sure you have installed the frontend, which only needs to happen once (see the last section of _Installation steps_ above).
