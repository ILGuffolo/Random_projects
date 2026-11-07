
import json
from tokenizer import Tokenizer


def load_dataset(path="data/conversations.json"):
    with open(path, "r", encoding="utf-8") as file:
        conversations = json.load(file)

    tokenizer = Tokenizer()

    sentences = []

    for question, answer in conversations:
        sentences.append(question)
        sentences.append(answer)

    tokenizer.build_vocabulary(sentences)

    return conversations, tokenizer
