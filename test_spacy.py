import spacy

nlp = spacy.load("en_core_web_sm")

doc = nlp("Python, FastAPI, Docker and AWS are great skills.")

for token in doc:
    print(token.text, token.lemma_)