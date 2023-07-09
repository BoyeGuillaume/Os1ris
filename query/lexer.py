from ply.lex import lex

# Error class
class LexicalError(Exception):
    pass

class QueryLexer(object):
    # List of token names, this is always required
    reserved = {
        'AND' : 'AND',
        'OR'  : 'OR',
        'XOR' : 'XOR',
        'NOT' : 'NOT',
        'LIKE': 'LIKE',

        # Following are just to ensures that no one can access those sql keywords
        'SELECT': 'SELECT',
        'FROM': 'FROM',
        'WHERE': 'WHERE',
        'GROUP': 'GROUP'
    }

    tokens = [
        'NUMBER',
        'STRING',
        'BINCOMP',
        'CONCAT',
        'ID',
        'BOOLEAN',
    ] + list(reserved.values())

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'

    # Literals can be specified by defining a variable literals 
    literals = [ '+', '-', '*', '/', '(', ')', ',' ]

    # Regular expression rules for simple tokens
    t_BINCOMP = r'([><]=?)|([!=]=)'
    t_CONCAT = r'\|\|'

    def t_ID(self, t):
        r'[a-zA-Z][A-Za-zÀ-ÖØ-öø-ÿ0-9\_]*(\.[a-zA-Z][A-Za-zÀ-ÖØ-öø-ÿ0-9\_]*)*'
        if t.value.upper() in ['TRUE', 'FALSE']:
            t.type = 'BOOLEAN'
            t.value = ('BOOLEAN', t.value.upper())
        else:
            t.type = QueryLexer.reserved.get(t.value, 'ID')
        return t
    
    def t_NUMBER(self,t):
        r'([1-9]\d*|0)(\.\d*)?'
        t.value = ('float', float(t.value))
        return t

    def t_STRING(self,t):
        r'\"([^\"\\]|\\.)*\"'
        t.value = ('string', t.value) # t.value[1:-1].encode('utf-8').decode('unicode_escape')
        return t

    # Error handling rule
    def t_error(self,t):
        raise LexicalError("Unexpected character '{}'".format(t.value[0]))
    
    # Build the lexer
    def build(self,**kwargs):
        self.lexer = lex(module=self, **kwargs)

    # Test it output
    def tokenize(self,data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok: 
                break
            yield tok


