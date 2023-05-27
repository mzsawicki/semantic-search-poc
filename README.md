# Semantic search implementation
## Proof of concept

### Introduction
This repository contains a p-o-c implementation of semantic search
using ElasticSearch index and NLP model for text embeddings. Example
data which is used are feline diseases articles scrapped from Wikipedia,
although you can provide your own list of articles to scrap
(see section "providing your own data"). The app is accessed through
a web API documented below in the "API" section. By default, the API
is hosted at: `http://0.0.0.0:8080` (you can change the port in the `config.yml` file)

### Installation and running
Install required packages
```shell
pip install -r requirements.txt
```
When you run the app first for the first time, or when
you provide a new list of articles to index, you need to
request re-indexing:
```shell
curl --location --request POST 'http://0.0.0.0:8080/reindex'
```
Then run:
```shell
python app.py
```

### API
```
POST /reindex
```
Scraps Wikipedia articles by titles placed in selected file (see: `config.yml`, `articles`/`file` section)
and indexes them in ElasticSearch along with their text embeddings computed
by chosen NLP model (`config.yml`, `tensorflow_hub`/`model_url`).

```
POST /search
```
```json
{
  "query": "string"
}
```
Performs semantic search on indexed articles, by the provided `query`.

### Providing your own data
You can provide your own list of articles to scrap and index. Simply put a .txt file
containing lines of Wikipedia article titles inside the main directory and provide its name
in `config.yml`, section `articles`/`file`. Then, request reindexing.

### Using other NLP model
By default, the app uses Universal Sentence Encoder v.4 to create text embeddings.
You can choose any other model available in Tensorflow Hub. Just change section `tensorflow_hub`/`model_url`
setting in `config.yml`
