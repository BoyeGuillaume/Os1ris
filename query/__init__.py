from query.lexer import QueryLexer
from query.parser import filter_parser, value_parser
from query.safe_sql import sql_query
from query.evaluator import simplify
import random

default_safe_function = [
    'LENGTH',
    'LOWER',
    'REPLACE',
    'UPPER',
    'ABS',
    'MAX',
    'MIN',
    'RANDOM',
    'ROUND',
    'DATE',
    'NOW',
    'STRFTIME',
    'COALESCE',
    'IIF'
]

def LENGTH_(s):
    return len(s)

def LOWER_(s):
    return s.lower()

def REPLACE_(s):
    return s.replace()

def UPPER_(s):
    return s.upper()

def ABS_(f):
    return abs(f)

def MAX_(fa, fb):
    return max(fa, fb)

def MIN_(fa, fb):
    return min(fa, fb)

def RANDOM_():
    return random.randint(-9223372036854775808, +9223372036854775807)

def ROUND_(fx):
    return round(fx)

def IIF_(bcond, _a, _b):
    return _a if bcond else _b

def sanitize_safe_sql_filter(string, safe_identifier, safe_function = default_safe_function):
    lexer = QueryLexer()
    lexer.build()

    return sql_query(filter_parser.parse(string), 0, { 'safe_identifier': safe_identifier, 'safe_function': safe_function })

def sanitize_safe_sql_value(string, safe_identifier, safe_function = default_safe_function):
    lexer = QueryLexer()
    lexer.build()

    return sql_query(value_parser.parse(string), 0, { 'safe_identifier': safe_identifier, 'safe_function': safe_function })

def evaluate(string, context = {}):
    lexer = QueryLexer()
    lexer.build()

    _context = {}
    for key in context:
        value = context[key]
        if isinstance(value, float):
            _context[key] = ('float', value)
        elif isinstance(value, int):
            _context[key] = ('float', value)
        elif isinstance(value, str):
            _context[key] = ('string', value)
        elif isinstance(value, bool):
            _context[key] = ('BOOLEAN', "TRUE" if value else "FALSE")
        else:
            raise Exception(f'Unknown context type: {type(value)}')

    _fn_context = {
        'LENGTH': LENGTH_,
        'LOWER': LOWER_,
        'UPPER': UPPER_,
        'ABS': ABS_,
        'MAX': MAX_,
        'MIN': MIN_,
        'RANDOM': RANDOM_,
        'ROUND': ROUND_,
        'IIF': IIF_
    }

    return simplify(value_parser.parse(string), 0, { 'values': _context, 'fn': _fn_context })
