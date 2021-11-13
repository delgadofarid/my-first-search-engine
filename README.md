# my-first-search-engine
Demo on how to build a search engine from the scratch!

## Requirements

- Docker - see: https://docs.docker.com/get-docker/
- Python >= 3.8

## How to install?

1. Install Jupyter Notebook:

```bash
$ pip install notebook
```

2. Run jupyter notebook from the root folder:

```bash
$ cd my-first-search-engine/notebook
$ jupyter notebook
```

3. Run each cell in the notebook `notebook/pipeline.ipynb`: The first couple of cells will install all the requirements in `notebook/requirements.txt`, build and start a docker container containing an Elasticsearch instance + Kibana; the cells beyond will process the content, store it in Elasticsearch and run performance validations.


## How to run browser app?

```bash
$ cd my-first-search-engine
$ env FLASK_APP=src/app python -m flask run
```