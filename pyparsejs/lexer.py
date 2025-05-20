# lexer.py
import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "value"])

token_spec = [
    ('NUMBER',  r'\d+(\.\d+)?'),
    ('STRING',  r'"[^"]*"|\'[^\']*\''),   # Matches both "..." and '...'
    ('ID',      r'[A-Za-z_]\w*'),
    ('OP',      r'[+\-*/=<>!]+'),
    ('DOT',     r'\.'),
    ('PUNCT',   r'[{}\[\]().,;:]'),
    ('SKIP',    r'[ \t]+'),
    ('NEWLINE', r'\n'),
]

tok_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in token_spec)
master_pat = re.compile(tok_regex)

def tokenize(code: str):
    tokens = []
    for match in master_pat.finditer(code):
        kind = match.lastgroup
        value = match.group()

        if kind == 'SKIP':
            continue

        if kind == 'STRING':
            # Strip the surrounding quotes: "Alice" → Alice
            quote_char = value[0]
            value = value[1:-1].encode().decode("unicode_escape")  # Handle \n, \t, etc.

        tokens.append(Token(kind, value))
    return tokens
