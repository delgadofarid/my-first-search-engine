from elasticsearch import Elasticsearch


def search_candidates(user_question, index_name="wikibooks-search-index", size=20, es=Elasticsearch()):
    return None