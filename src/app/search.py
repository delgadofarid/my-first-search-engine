import re
from elasticsearch import Elasticsearch, helpers
from itertools import islice

# initialize Elasticsearch client
es = Elasticsearch()


def first_n(iterable, n):
    return islice(iterable, 0, n)


def format_es_response(user_question, es_candidates):
    results = list()
    for c in es_candidates:
        par = dict()
        par['questionText'] = user_question
        par['bookTitle'] = c['_source']['bookTitle']
        par['paragraphText'] = c['_source']['paragraphText']
        par['esScore'] = c['_score']
        par['paragraphId'] = c['_source']['paragraphId']
        par['bookURL'] = c['_source']['bookURL']
        par['bookId'] = c['_source']['bookId']
        results.append(par)
    return results


def search_candidates(user_question, index_name="wikibooks-search-index", size=20, es=Elasticsearch()):
    match_queries = [
        {"match": {"bookTitle": user_question}},
        {"match": {"paragraphText": user_question}}
    ]
    quoted_text = re.findall('"([^"]*)"', user_question)
    for text in quoted_text:
        match_queries.append({"match_phrase": {"bookTitle": text}})
        match_queries.append({"match_phrase": {"paragraphText": text}})

    es_query = {
        "query": {
            "bool": {
                "should": match_queries
            }
        }
    }

    results = helpers.scan(es, query=es_query, index=index_name, preserve_order=True)
    results = first_n(results, size)
    return format_es_response(user_question, results)
