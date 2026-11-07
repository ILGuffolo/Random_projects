
import re


class Tokenizer:
    PAD = "<PAD>"
    UNK = "<UNK>"
    SOS = "<SOS>"
    EOS = "<EOS>"

    def __init__(self):
        self.word_to_id = {
            self.PAD: 0,
            self.UNK: 1,
            self.SOS: 2,
            self.EOS: 3
        }

        self.id_to_word = {
            0: self.PAD,
            1: self.UNK,
            2: self.SOS,
            3: self.EOS
        }

    def tokenize(self, text):
        return re.findall(r"\w+|[^\w\s]", text.lower())

    def build_vocabulary(self, sentences):
        words = set()

        for sentence in sentences:
            words.update(self.tokenize(sentence))

        for word in sorted(words):
            if word not in self.word_to_id:
                idx = len(self.word_to_id)
                self.word_to_id[word] = idx
                self.id_to_word[idx] = word

    def encode(self, text):
        tokens = self.tokenize(text)

        ids = [
            self.word_to_id.get(word, 1)
            for word in tokens
        ]

        return [2] + ids + [3]

    def decode(self, ids):
        words = []

        for idx in ids:
            if idx == 3:
                break

            if idx > 3:
                words.append(self.id_to_word.get(idx, self.UNK))

        text = " ".join(words)

        # Basic punctuation formatting
        text = re.sub(r"\s+([.,!?])", r"\1", text)

        return text
