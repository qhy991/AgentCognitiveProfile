"""Lexer — tokenizes template source into a stream of tokens."""

import re

TOKEN_SPEC = [
    ("VAR_START", r"\{\{"),       # {{
    ("VAR_END", r"\}\}"),         # }}
    ("BLOCK_START", r"\{%"),      # {%
    ("BLOCK_END", r"%\}"),        # %}
    ("TEXT", r"(?:(?!\{\{|\}\}|\{%|%\}).)+"),  # anything not starting a special token
]

TOKEN_RE = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))


def tokenize(source):
    """Tokenize template source into a list of (type, value) tuples."""
    tokens = []
    for m in TOKEN_RE.finditer(source):
        kind = m.lastgroup
        value = m.group()
        tokens.append((kind, value))
    return tokens