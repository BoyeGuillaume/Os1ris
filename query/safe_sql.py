class SqlException(Exception):
    pass

def sql_query(ast, depth = 0, context = {}):
    if depth >= 20:
        raise SqlException('Max depth recursion limit reached')

    match ast:
        case ('==', op1, op2):
            return '{} == {}'.format(sql_query(op1, depth + 1, context), sql_query(op2, depth + 1, context))
        case ('string', value):
            return value
        case ('float', value):
            return str(value)
        case ('id', value):
            if value not in context['safe_identifier']:
                raise SqlException(f'Unsafe identifier "{value}"')
            return value
        case ('NOT', value):
            return '(NOT {})'.format(sql_query(value, depth + 1, context))
        case ('call', function, arglist):
            if function not in context['safe_function']:
                raise SqlException(f'Unsafe function "{value}"')
            args = ', '.join(sql_query(x, depth + 1, context) for x in arglist)
            return f'{function.upper()}({args})'
        case ('CONCAT', op1, op2):
            return '(' + sql_query(op1, depth + 1, context) + ' || ' + sql_query(op2, depth + 1, context) + ')'
        case (operator, op1, op2):
            return '(' + sql_query(op1, depth + 1, context) + ' ' + operator + ' ' + sql_query(op2, depth + 1, context) + ')'
        case ('BOOLEAN', value):
            return value.upper()

    raise SqlException(f'Should not be reached: {ast}')
