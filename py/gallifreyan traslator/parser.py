class Unit:
    def __init__(self, text, unit_type="consonant"):
        self.text = text              # "B", "O", "TH", etc.
        self.unit_type = unit_type    # consonant / vowel / punctuation
        self.attached_to = None       # reference to another Unit
        self.modifiers = {}           # dots, lines later

    def __repr__(self):
        return f"{self.text}"


class Word:
    def __init__(self):
        self.units = []

    def add(self, unit):
        self.units.append(unit)

    def __repr__(self):
        return "Word(" + ", ".join(str(u) for u in self.units) + ")"


class Sentence:
    def __init__(self):
        self.words = []

    def add(self, word):
        self.words.append(word)
    
    def __repr__(self):
        return str(self.words)

GROUPS = {
    "DIGRAPHS" : [
        "ch", "nd", "ph", "wh", "sh", "nt", "th", "gh", "qu", "ng"
    ],

    "CONSONANTS" : [
        "b", "d", "g", "h", "f", "j", "k", "l", "c", "n", "p", "m", "t", "r", "v", "w", "s", "y", "z", "q", "x", 
    ],
    
    "VOWELS" : ["a", "e", "i", "o", "u"], 

    "PUNCTUATION" : ["'", ".", ",", "!", "?", "\"", "-", ";", ":", "&"]
    }

def tokenize(word):
    result = []
    i = 0

    while i < len(word):
        match = None

        for group in GROUPS.values():  # priority order
            for token in group:
                if word.startswith(token, i):
                    match = token
                    break
            if match:
                break

        if match:
            result.append(match)
            i += len(match)
        else:
            # fallback: single character
            print(f"unrecognized charachter: {word[i]}")
            result.append("0")
            i += 1

    return result

def build_units(tokens):
    units = []
    last_consonant = None

    for t in tokens:
        if t.lower() in GROUPS["VOWELS"]: #Vowel
            unit = Unit(t, "vowel")

            if last_consonant:
                unit.attached_to = last_consonant
            units.append(unit)

        elif t in GROUPS["PUNCTUATION"]: #Punctuation
            units.append(Unit(t, "punctuation"))
        
        elif t in GROUPS["DIGRAPHS"]: #Digraph
            unit = Unit(t, "digraph")
            units.append(unit)
            last_consonant = unit

        else:
            unit = Unit(t, "consonant")
            units.append(unit)
            last_consonant = unit

    return units

def parse_text(text):
    sentence = Sentence()

    words_raw = text.split()

    for w in words_raw:
        tokens = tokenize(w)
        units = build_units(tokens)

        word = Word()
        for u in units:
            word.add(u)

        sentence.add(word)

    return sentence

