from query import sanitize_safe_sql_filter, sanitize_safe_sql_value, evaluate

mode = 'evaluator'

while True:
    try:
        text = input(f'exec[{mode}] $ ')

        if text == 'switch filter':
            mode = 'filter'
            continue
        elif text == 'switch value':
            mode = 'value'
            continue
        elif text == 'switch evaluator':
            mode = 'evaluator'
            continue
        elif text == 'exit':
            break

        if mode == 'filter':
            print(sanitize_safe_sql_filter(text, ['balance', 'amount', 'value']))
        elif mode == 'value':
            print(sanitize_safe_sql_value(text, ['balance', 'amount', 'value']))
        elif mode == 'evaluator':
            print(evaluate(text, { 'balance': 50.1, 'test': "text" }))


    except Exception as e:
        print(f'Exception: {e}')