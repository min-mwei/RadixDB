import sqlparse
from sqlparse import sql, tokens as T
from sqlparse.sql import IdentifierList, Identifier, Function, Token


def rewrite_show_html(tokens):
    print("ftks:", tokens)
    params = []
    capture = False
    for tok in tokens:
        val = tok[1]
        if val == '(':
            capture = True
        elif val == ')':
            capture = False
        if capture:
            if tok[0] == T.Name:
                params.append(val)
    print("params:", params)
    return "html(jsonb_agg(jsonb_build_object(" + ",".join(params) + ")))"

func_map = {
    'show_html': rewrite_show_html
    }
def rewrite_sql(sql):
    tokens = []
    capture = -1
    func_toks = []
    func = None
    try:
        for token in sqlparse.parse(sql)[0].flatten():
            if token.ttype == T.Name and token.value in func_map:
                func_toks.append((token.ttype, token.value))
                capture = 0
                func = func_map[token.value]
            elif capture >= 0 and token.ttype == T.Punctuation and token.value == '(':
                capture += 1
                func_toks.append((token.ttype, token.value))
            elif capture >= 0 and token.ttype == T.Punctuation and token.value == ')':
                capture -= 1
                func_toks.append((token.ttype, token.value))
                if capture == 0:
                    capture -= 1
                    tokens.append(func(func_toks))
            elif capture > 0:
                if token.ttype != T.Whitespace:
                    func_toks.append((token.ttype, token.value))
            else:
                tokens.append(token.value)
    except StopIteration:
        raise ValueError("Not enough parameters provided")
    print(tokens)
    print(func)
    return " ".join(tokens)
