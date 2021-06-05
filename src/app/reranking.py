from tqdm import tqdm

# initilize reranking models
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

# Sequence Classification Model
tokenizer = AutoTokenizer.from_pretrained("amberoad/bert-multilingual-passage-reranking-msmarco")
model = AutoModelForSequenceClassification.from_pretrained("amberoad/bert-multilingual-passage-reranking-msmarco")

# Extractive Question Answering Model - for Snippets
nlp = pipeline(
    'question-answering',
    model='mrm8488/distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es',
    tokenizer=(
        'mrm8488/distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es',
        {"use_fast": False}
    )
)


def normalize_pairs(pairs):
    QUOTES_TRANSL_TABLE = {ord(x): ord(y) for x, y in zip(u"‘’´“”", u"'''\"\"")}

    def _fix_quotes(text):
        return text.translate(QUOTES_TRANSL_TABLE)

    def _normalize_query(query):
        return _fix_quotes(" ".join(query.split()).lower().replace("¿", "").replace("?", ""))

    def _normalize_paragraph(paragraph):
        return _fix_quotes(" ".join(paragraph.split()))

    return [(_normalize_query(row['questionText']),
             _normalize_paragraph(row['paragraphText'])) for row in pairs]


def encode_pairs(pairs_to_encode):
    return tokenizer.batch_encode_plus(
        normalize_pairs(pairs_to_encode),
        max_length=512,
        truncation="longest_first",
        return_tensors='pt',
        padding="longest"
    )


def rank_paragraphs(pairs):
    print(f"rank_paragraphs...")
    cpu_batch_size = 5
    pairs.sort(key=lambda x: (len(x["questionText"]) + len(x["paragraphText"])))
    result_tensors = list()
    for batch in tqdm([pairs[x:x + cpu_batch_size] for x in range(0, len(pairs), cpu_batch_size)]):
        encoded_pairs = encode_pairs(batch)
        # use Model to assign sequence (question -> passage) classification score
        predicted = model(**encoded_pairs)[0].softmax(dim=1)[:, 1]
        result_tensors.append((batch, predicted.to(device="cpu", non_blocking=True)))

    output = list()
    for batch, predicted in result_tensors:
        extracted_info = predicted.tolist()
        for index, score in enumerate(extracted_info):
            output.append({
                "questionText": batch[index]["questionText"],
                "bookId": batch[index]["bookId"],
                "bookTitle": batch[index]["bookTitle"],
                "bookURL": batch[index]["bookURL"],
                "paragraphId": batch[index]["paragraphId"],
                "paragraphText": batch[index]["paragraphText"],
                "sequenceScore": score
            })
    ranked_paragraphs = sorted(output, key=lambda item: item['sequenceScore'], reverse=True)
    return ranked_paragraphs


def get_answers_with_snippets(ranked_paragraphs, snippet_threshold=0.8):
    print(f"get_answers_with_snippets...")
    # get top parragraph for each document
    top_paragraph_by_book = dict()
    for par in ranked_paragraphs:
        if par['bookId'] in top_paragraph_by_book:
            continue
        top_paragraph_by_book[par['bookId']] = par
    top_answer_paragraphs = list(top_paragraph_by_book.values())
    # assign snippets
    for par in tqdm(top_answer_paragraphs):
        # use Model to extract answer from paragraph and assign the answer score
        if par['sequenceScore'] > snippet_threshold:
            extracted_answer = nlp(question=par['questionText'], context=par['paragraphText'])
            if extracted_answer['score'] >= snippet_threshold:
                par['answerScore'] = extracted_answer['score']
                par['answerStart'] = extracted_answer['start']
                par['answerEnd'] = extracted_answer['end']
                par['answerText'] = extracted_answer['answer']
    return top_answer_paragraphs
