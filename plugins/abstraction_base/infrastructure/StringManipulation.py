from re import sub

from unicodedata import normalize, category

def normalize_string(string: str):
    return sub(r'[^A-Za-z0-9 \-]+', '', ''.join(c for c in normalize('NFD', string) if category(c) != 'Mn'))