import ply.yacc as yacc
from query.lexer import QueryLexer

tokens = QueryLexer.tokens
literals = QueryLexer.literals

# Error class
class SyntaxError(Exception):
    pass

# Defines the grammar
def p_expr_term(p):
    'expression : term'
    p[0] = p[1]

def p_binop_par(p):
    '''
        bin_expr_term : '(' bin_expr ')'
    '''
    p[0] = p[2]

def p_binop(p):
    '''
        bin_expr_term : expression BINCOMP expression
                      | expression LIKE expression
        bin_expr      : bin_expr AND bin_expr
                      | bin_expr OR bin_expr
                      | bin_expr XOR bin_expr
        expression    : expression '+' term
                      | expression '-' term
                      | expression CONCAT term
        term          : term '*' factor
                      | term '/' factor
    '''
    p[0] = (p[2], p[1], p[3])

def p_unary(p):
    '''
        bin_expr   : NOT bin_expr_term
    '''
    p[0] = (p[1], p[2])

def p_term_factor(p):
    'term : factor'
    p[0] = p[1]

def p_factor_id(p):
    '''
        factor : ID
    '''
    p[0] = ('id', p[1])
    
def p_identity(p):
    '''
        bin_expr : bin_expr_term
                 | BOOLEAN
        term     : STRING
        factor   : NUMBER
                 | function
    '''
    'term : STRING'
    p[0] = p[1]

def p_factor_expr(p):
    '''
        factor : '(' expression ')'
    '''
    p[0] = p[2]

def p_function(p):
    '''
        function : ID '(' arglist ')'
    '''
    p[0] = ('call', p[1], p[3])

def p_arglist_empty(p):
    'arglist : '
    p[0] = []

def p_arglist2(p):
    '''
        arglist : expression
                | bin_expr
    '''
    p[0] = [p[1]]

def p_arglist(p):
    '''
        arglist : arglist ',' expression
                | arglist ',' bin_expr
    '''
    p[0] = p[1] + [p[3]]


def p_error(p):
    raise SyntaxError('Syntax error at token: {} at {}:{}'.format(p.type, p.lineno, p.lexpos))

# Build the parser
filter_parser = yacc.yacc(start = 'bin_expr')
value_parser = yacc.yacc(start = 'expression')
