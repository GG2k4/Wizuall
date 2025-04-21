import ply.yacc as yacc
from wizual_lexer import tokens

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD', 'AT'),
)

def p_program(p):
    'program : statement_list'
    p[0] = ("program", p[1])

def p_statement_list_multiple(p):
    'statement_list : statement_list statement'
    p[0] = p[1] + [p[2]]

def p_statement_list_single(p):
    'statement_list : statement'
    p[0] = [p[1]]

def p_statement(p):
    '''statement : assignment_stmt
                 | void_function_call_stmt
                 | while_stmt
                 | if_stmt'''
    p[0] = p[1]

def p_void_function_call_stmt(p):
    'void_function_call_stmt : expression SEMICOLON'
    p[0] = p[1]

def p_assignment_stmt(p):
    'assignment_stmt : IDENTIFIER ASSIGN expression SEMICOLON'
    p[0] = ("assign", p[1], p[3])

def p_while_stmt(p):
    'while_stmt : WHILE LPAREN bool_expr RPAREN block'
    p[0] = ("while", p[3], p[5])

def p_if_stmt(p):
    'if_stmt : IF LPAREN bool_expr RPAREN block'
    p[0] = ("if", p[3], p[5])

def p_block(p):
    'block : LBRACE statement_list RBRACE'
    p[0] = ("block", p[2])

def p_bool_expr(p):
    '''bool_expr : expression EQ expression
                 | expression NE expression
                 | expression LT expression
                 | expression GT expression
                 | expression LE expression
                 | expression GE expression'''
    p[0] = ("bool", p[2], p[1], p[3])

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MOD expression
                  | expression AT expression'''
    p[0] = ("binop", p[2], p[1], p[3])

def p_expression_postfix(p):
    'expression : postfix_expr'
    p[0] = p[1]

def p_postfix_expr(p):
    'postfix_expr : primary_expr slice_list_opt'
    node = p[1]
    for sl in p[2]:
        node = ("slice", node, sl)
    p[0] = node

def p_slice_list_opt_empty(p):
    'slice_list_opt :'
    p[0] = []

def p_slice_list_opt_nonempty(p):
    'slice_list_opt : slice_list'
    p[0] = p[1]

def p_slice_list_single(p):
    'slice_list : slice'
    p[0] = [p[1]]

def p_slice_list_multiple(p):
    'slice_list : slice_list slice'
    p[0] = p[1] + [p[2]]

def p_slice(p):
    'slice : LBRACKET range_expr RBRACKET'
    p[0] = p[2]

def p_range_expr_range(p):
    'range_expr : NUMBER COLON NUMBER'
    p[0] = ("range", p[1], p[3])

def p_range_expr_single(p):
    'range_expr : NUMBER'
    p[0] = ("index", p[1])

def p_primary_expr_func_call(p):
    'primary_expr : IDENTIFIER LPAREN arg_list RPAREN'
    p[0] = ("call", p[1], p[3])

def p_primary_expr_number(p):
    'primary_expr : NUMBER'
    p[0] = ("number", p[1])

def p_primary_expr_identifier(p):
    'primary_expr : IDENTIFIER'
    p[0] = ("var", p[1])

def p_primary_expr_string(p):
    'primary_expr : STRING'
    p[0] = ("string", p[1])

def p_primary_expr_paren(p):
    'primary_expr : LPAREN expression RPAREN'
    p[0] = p[2]

def p_primary_expr_list(p):
    'primary_expr : list_literal'
    p[0] = p[1]

def p_primary_expr_table(p):
    'primary_expr : table_literal'
    p[0] = p[1]

def p_list_literal_nonempty(p):
    'list_literal : LBRACKET expression_list RBRACKET'
    p[0] = ("list", p[2])

def p_list_literal_empty(p):
    'list_literal : LBRACKET RBRACKET'
    p[0] = ("list", [])

def p_expression_list_multiple(p):
    'expression_list : expression_list COMMA expression'
    p[0] = p[1] + [p[3]]

def p_expression_list_single(p):
    'expression_list : expression'
    p[0] = [p[1]]

def p_table_literal(p):
    'table_literal : TABLE LPAREN table_params RPAREN'
    p[0] = ("table", p[3])

def p_table_params_multiple(p):
    'table_params : table_params COMMA table_param'
    d = p[1]
    d.update(p[3])
    p[0] = d

def p_table_params_single(p):
    'table_params : table_param'
    p[0] = p[1]

def p_table_param(p):
    'table_param : IDENTIFIER ASSIGN expression'
    p[0] = {p[1]: p[3]}

def p_arg_list_empty(p):
    'arg_list :'
    p[0] = []

def p_arg_list_nonempty(p):
    'arg_list : expression_list'
    p[0] = p[1]

def p_error(p):
    if p:
        raise SyntaxError(f"Unexpected token '{p.value}' at line {p.lineno}")
    else:
        raise SyntaxError("Unexpected end of input")

parser = yacc.yacc()