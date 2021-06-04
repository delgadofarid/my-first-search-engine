from flask import Flask, render_template, request, make_response
from app.search import search_candidates
from app.reranking import rank_paragraphs, get_answers_with_snippets

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('hello.html', name="Farid")


# @app.route('/', methods=['GET', 'POST'])
def search():
    # obtener valor "search_terms"

    # si no tiene valor, renderiza la página sin resultados
    # si tiene valor busca y rederiza y responde con resultados
    return render_template('search.html')