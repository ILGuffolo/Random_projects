player_synonyms = ["player", "self", "me", "myself"]

def article(string):
    """Return the indefinite article appropriate to the written spelling of a string. Helper function for the more-frequently-useful with_article.

This is defined on strings, not on Item names, so that it can be used in other parts of the program.
For an example, see how GameRunner handles "look X" when X is not an object that's present.

Caveats: does not correctly handle words which orthographically begin with a vowel but are pronounced beginning with a consonant, e.g. 'university'.
Also does not correctly handle spelled-out pronunciation of abbreviations, e.g. in English you say 'an SST' but this function will return 'a SST'.""" 
    if string[0] in "aeiou":
        return "an"
    else:
        return "a"

def with_article(string):
    "Returns :string: preceded by appropriate article. See article function."
    return " ".join([article(string), string])

def format_string_list(strings):
    "Returns :strings: formatted with English list conventions."
    "Used for displaying inventory and other player-facing lists."
    count = len(strings)
    if count > 2:
        listing = ", ".join([with_article(i) for i in strings[:-1]])
        # isolate the last item for special printing
        last = strings.pop()
        listing += " and " + with_article(last)
        strings.append(last)
        return listing
    elif count > 1:
        return with_article(strings[0]) + " and " + with_article(strings[1])
    else:
        return with_article(strings[0])
