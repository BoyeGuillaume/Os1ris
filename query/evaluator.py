from inspect import signature

class RuntimeException(Exception):
    pass

def simplify(ast, depth = 0, context = {}):
    simplify_ = lambda x: simplify(x, depth + 1, context)

    if depth >= 20:
        raise RuntimeException('Max depth recursion exceeded, aborting.')

    match ast:
        case (cmp, op1, op2) if cmp in ['==', '>=', '<=', '!=', '>', '<']:
            t1, s1 = simplify_(op1)
            t2, s2 = simplify_(op2)

            assert t1 == 'float'
            assert t2 == 'float'

            match cmp:
                case '==':
                    return ('BOOLEAN', abs(s1 - s2) < 1e-3)
                case '!=':
                    return ('BOOLEAN', abs(s1 - s2) >= 1e-3)
                case '>=':
                    return ('BOOLEAN', s1 >= s2)
                case '<=':
                    return ('BOOLEAN', s1 <= s2)
                case '>':
                    return ('BOOLEAN', s1 > s2)
                case '<':
                    return ('BOOLEAN', s1 < s2)
                
        case (binop, op1, op2) if binop in ['AND', 'OR', 'XOR']:
            t1, s1 = simplify_(op1)
            t2, s2 = simplify_(op2)

            assert t1 == 'BOOLEAN'
            assert t2 == 'BOOLEAN'

            match cmp:
                case 'AND':
                    return ('BOOLEAN', s1 and s2)
                case 'OR':
                    return ('BOOLEAN', s1 or s1)
                case 'XOR':
                    return ('BOOLEAN', (s1 or s2) and not (s1 and s2))
        
        case ('call', name, args):
            fn = context['fn'][name]
            sig = signature(fn)
            eArgs = [simplify_(i) for i in args]
    
            assert len(sig.parameters) == len(eArgs)
            for id, param in enumerate(sig.parameters):
                ty, val = eArgs[id]
                if param.startswith('f'):
                    assert ty == 'float'

                if param.startswith('s') or ty == 'string':
                    assert ty == 'string'
                    val = val[1:-1]

                if param.startswith('b'):
                    assert ty == 'BOOLEAN'

                eArgs[id] = val

            result = fn(*eArgs)
            if isinstance(result, float):
                return ('float', result)
            if isinstance(result, int):
                return ('float', result)
            elif isinstance(result, str):
                return ('string', '"' + result + '"')
            elif isinstance(result, bool):
                return ('BOOLEAN', result)
            else:
                assert False

        case ('id', value):
            return context['values'][value]
        case ('float', value):
            return ('float', value)
        case ('string', value):
            return ('string', value)
        case ('BOOLEAN', value):
            return ('BOOLEAN', True if value == "TRUE" else False)
        case (opx, op1, op2) if opx in ['+', '-', '*', '/']:
            t1, s1 = simplify_(op1)
            t2, s2 = simplify_(op2)

            assert t1 == 'float'
            assert t2 == 'float'

            match opx:
                case '+':
                    return ('float', s1 + s2)
                case '-':
                    return ('float', s1 - s2)
                case '*':
                    return ('float', s1 * s2)
                case '/':
                    return ('float', s1 / s2)
                
        case ('||', op1, op2):
            t1, s1 = simplify_(op1)
            t2, s2 = simplify_(op2)

            assert t1 == 'string'
            assert t2 == 'string'

            return ('string', s1[:-1] + s2[1:])
        
    raise Exception(f'Unknown abstract tree: {ast}')
        