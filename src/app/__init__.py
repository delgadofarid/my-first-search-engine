from flask import Flask, render_template, request, make_response
from app.search import search_candidates
from app.reranking import rank_paragraphs, get_answers_with_snippets

app = Flask(__name__)


@app.route('/hello')
def hello_world():
    return render_template('hello.html', name="Farid")


@app.route('/', methods=['GET', 'POST'])
def search():
    search_terms = request.args.get('search_terms', None)

    if not search_terms:
        return render_template('search.html')

    search_results = search_candidates(search_terms)
    search_results = rank_paragraphs(search_results)
    search_results = get_answers_with_snippets(search_results)
    for result in search_results:
        if "answerText" in result:
            # if result includes snippet
            start = result['answerStart']
            end = result['answerEnd']
            htmlSnippet = "<p>" + result['paragraphText'][:start] + "<mark>" + result['paragraphText'][start:end] + "</mark>" + result['paragraphText'][end:] + "</p>"
        else:
            htmlSnippet = "<p>" + result['paragraphText'] + "</p>"
        result['htmlSnippet'] = htmlSnippet

    resp = make_response(render_template('search.html', results=search_results))
    return resp
