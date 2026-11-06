import random
import re
import os
    
# --- Global memory for keywords ---
keyword_history  = {}
keyword_index = {}

KEYWORD_PATTERN = re.compile(r"%([A-Za-z0-9_]+)%")
MEMORY_PATTERN = re.compile(r"@([A-Za-z0-9_]+)@")
RANDOM_MEMORY_PATTERN = re.compile(r"\$([A-Za-z0-9_]+)\$")
BACKTRACK_PATTERN = re.compile(r"£([A-Za-z0-9_]+)£")

ADJ_CHANCE = 0.5
    
def random_line(filename: str) -> str:
    """Return a random non-empty line from a text file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            # File exists but has no lines → fallback
            return f"[No lines in {filename}]"
        return random.choice(lines)
    except FileNotFoundError:
        # File missing → fallback
        return f"[File {filename} not found]"


def adjective(keyword: str, value: str) -> str:
    """Randomly prepend or append an adjective from adj/keyword.txt"""
    if random.random() < ADJ_CHANCE:
        folder = os.path.dirname(os.path.abspath(__file__))
        adj_path = os.path.join(folder, "data", "adj", f"{keyword}.txt")
        try:
            with open(adj_path, "r", encoding="utf-8") as f:
                adjectives = [line.strip() for line in f if line.strip()]
            if adjectives:
                adj = random.choice(adjectives)
                value = f"{adj} {value}"
                
        except FileNotFoundError:
            pass  # silently ignore if adjective file not found
    return value

def Story(text: str, max_depth: int = 10):
    """
    Substitute:
    %keyword% -> new value + append to history
    @keyword@ -> most recent value (or generate if empty)
    $keyword$ -> random previous value from history (or generate if empty)
    £keyword£ → index-1, return that value
    """
    result = text

    for _ in range(max_depth):

        # --- %keyword% ---
        def replace_keyword(m):
            keyword = m.group(1)
            value = random_line(f"data/{keyword}.txt")
            value = adjective(keyword, value)
            keyword_history.setdefault(keyword, []).append(value)
            keyword_index[keyword] = len(keyword_history[keyword]) - 1
            return value

        result = KEYWORD_PATTERN.sub(replace_keyword, result)

        # --- @keyword@ ---
        def replace_memory(m):
            keyword = m.group(1)
            hist = keyword_history.get(keyword, [])
            idx = keyword_index.get(keyword, 0)
            if hist:
                return hist[idx]
            else:
                # generate if empty
                value = random_line(f"data/{keyword}.txt")
                keyword_history.setdefault(keyword, []).append(value)
                keyword_index[keyword] = len(keyword_history[keyword]) - 1
                return value

        result = MEMORY_PATTERN.sub(replace_memory, result)

        # --- $keyword$ ---
        def replace_random_memory(m):
            keyword = m.group(1)
            hist = keyword_history.get(keyword, [])
            if hist:
                return random.choice(hist)
            else:
                value = random_line(f"data/{keyword}.txt")
                keyword_history.setdefault(keyword, []).append(value)
                keyword_index[keyword] = len(keyword_history[keyword]) - 1
                return value

        result = RANDOM_MEMORY_PATTERN.sub(replace_random_memory, result)

        # --- £keyword£ ---
        def replace_backtrack(m):
            keyword = m.group(1)
            hist = keyword_history.get(keyword, [])
            if hist:
                idx = keyword_index.get(keyword, 0)
                idx = max(0, idx - 1)
                keyword_index[keyword] = idx
                return hist[idx]
            else:
                value = random_line(f"data/{keyword}.txt")
                keyword_history.setdefault(keyword, []).append(value)
                keyword_index[keyword] = len(keyword_history[keyword]) - 1
                return value

        result = BACKTRACK_PATTERN.sub(replace_backtrack, result)

        # Stop if no patterns left
        if not any(p.search(result) for p in [KEYWORD_PATTERN, MEMORY_PATTERN, RANDOM_MEMORY_PATTERN, BACKTRACK_PATTERN]):
            break

    return result

def adventure():
    print(Story("%start%"), "\n")
    while True :
        print(Story("1: %choice%\n2: %choice%\n3: %choice%\n4: %choice%\n"))
        input("you coose to: ")
        print(Story("\n%answer%\n"))
        print(Story("%adventure%\n"))
        
        
    
    