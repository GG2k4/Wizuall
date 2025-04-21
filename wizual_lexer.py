import ply.lex as lex

class LexError(Exception):
    pass

reserved = {'while': 'WHILE', 'table': 'TABLE', 'if': 'IF'}
tokens = (
    'NUMBER', 'IDENTIFIER', 'STRING',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'AT', 'ASSIGN',
    'SEMICOLON', 'COMMA', 'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE',
    'COLON', 'EQ', 'NE', 'LT', 'GT', 'LE', 'GE'
) + tuple(reserved.values())

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_MOD     = r'%'
t_AT      = r'@'
t_ASSIGN  = r'='
t_SEMICOLON = r';'
t_COMMA   = r','
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_COLON   = r':'
t_EQ      = r'=='
t_NE      = r'!='
t_LE      = r'<='
t_GE      = r'>='
t_LT      = r'<'
t_GT      = r'>'

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    raise LexError(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")

lexer = lex.lex()