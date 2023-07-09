from flask import Blueprint, request, session, g, abort, current_app
import sqlite3
import time
from utils import DatabaseHandle, intervals_list

blueprint = Blueprint('api', __name__)


def require_logged_in():
    if not 'uid' in session:
        abort(401, 'This features require to be logged in')

def require_access(aid, writeAccess = True, ownership = False):
    require_logged_in()
    if not get_db().has_access(session['uid'], aid, ownership):
        abort(403, 'Forbidden')

def require_budget_access(bid, writeAccess = True, ownership = False):
    require_logged_in()
    if not get_db().has_budget_access(session['uid'], bid, ownership):
        abort(403, 'Forbidden')

def require_fields(fields):
    for field in fields:
        if field not in request.form:
            abort(400, 'Missing required field: {}'.format(field))

def require_args(fields):
    for field in fields:
        if field not in request.args:
            abort(400, 'Missing required field')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
    return DatabaseHandle(db)


@blueprint.route('/api/create-account', methods=['POST'])
def create_account():
    require_logged_in()
    require_fields(['name', 'creation_date', 'currency', 'description'])

    try:
        uid = session['uid']
        name = request.form['name'].strip()
        creation_date = request.form['creation_date']
        currency = request.form['currency']
        description = request.form['description']

        if len(name) > 15:
            return {}, 500
        
        isSuccess, aid = get_db().create_account(uid, name, creation_date, currency, description)
        if isSuccess:  
            return { 'aid': aid }, 200
        else:
            return {}, 412

    except Exception as e:
        current_app.logger.error('Unhandled exception when trying to handle response {}'.format(e))

@blueprint.route('/api/delete-account', methods=['POST'])
def delete_account():
    require_logged_in()
    require_fields(['aid'])
    aid = request.form['aid']
    require_access(aid=aid, writeAccess=True, ownership=True)

    return get_db().delete_account(aid)

@blueprint.route('/api/list-accounts', methods=['GET'])
def list_accounts():
    require_logged_in()

    uid = session['uid']
    response = get_db().list_account(uid)

    return response, 200

@blueprint.route('/api/get-account', methods=['GET'])
def get_account():
    require_args(['aid'])
    aid = request.args['aid']
    require_access(aid, writeAccess=False)

    account = get_db().get_account(aid)
    account['balance'] = get_db().get_balance(aid)

    return account, 200

@blueprint.route('/api/create-transaction', methods=['POST'])
def create_transaction():
    require_logged_in()
    require_fields(['aid', 'amount', 'date', 'available_date', 'description'])
    require_access(request.form['aid'], writeAccess=True)

    tags = []
    if 'tags' in request.form:
        tags = request.form['tags'].split(',')

    if not get_db().create_transaction(session['uid'], request.form['aid'], request.form['amount'], request.form['date'], request.form['available_date'], request.form['description'], tags):
        return {}, 500
    
    return {}, 200

@blueprint.route('/api/get-transaction', methods=['GET'])
def get_transaction():
    require_logged_in()
    require_args(['aid', 'limit', 'offset'])
    require_access(request.args['aid'], writeAccess=False)
    
    search = None
    sort = None
    if 'search' in request.args:
        search = request.args['search']
    if 'order' in request.args and 'dir' in request.args:
        sort = (request.args['order'],request.args['dir'])

    return get_db().get_transaction(session['uid'], request.args['aid'], int(request.args['offset']), int(request.args['limit']), search = search, sort = sort)

@blueprint.route('/api/get-tags', methods=['GET'])
def get_tags():
    require_logged_in()

    return get_db().list_tags(session['uid'])

@blueprint.route('/api/update-tag', methods=['POST'])
def update_tag():
    require_logged_in()
    require_fields(['id', 'name', 'color'])

    return get_db().update_tag(session['uid'], request.form['id'], request.form['name'], request.form['color'])


@blueprint.route('/api/get-balance', methods=['GET'])
def get_balance():
    require_logged_in()
    require_args(['aid'])
    aid = request.args['aid']
    require_access(aid, writeAccess=False)

    return get_db().get_balance(aid)

@blueprint.route('/api/get-balance-history', methods=['GET'])
def get_balance_history():
    require_logged_in()
    require_args(['aid', 'interval'])
    aid = request.args['aid']
    require_access(aid, writeAccess=False)

    interval = request.args['interval']
    if interval not in ['month', 'trimester', 'semester', 'day', 'year']:
        abort(400, 'Bad Request')
    
    result = {
        'date': get_db().get_history(aid, interval, 'date'),
        'available_date': get_db().get_history(aid, interval, 'available_date')
    }

    return result

@blueprint.route('/api/delete-transaction', methods=['POST'])
def delete_transaction():
    require_logged_in()
    require_fields(['aid', 'id'])
    aid =  request.form['aid']
    id =  request.form['id']
    require_access(aid, writeAccess=True)

    get_db().delete_transaction(aid, id)
    return {}, 200

@blueprint.route('/api/update-transaction', methods=['POST'])
def update_transaction():
    require_logged_in()
    require_fields(['aid', 'id', 'field', 'value'])

    aid = int(request.form['aid'])
    id = int(request.form['id'])
    field = request.form['field']
    value = request.form['value']

    require_access(aid, writeAccess=True)

    if field not in ['available_date', 'date', 'amount']:
        abort(400, 'Bad Request')

    get_db().update_transaction(aid, id, field, value)
    return {}, 200

@blueprint.route('/api/create-budget', methods=['POST'])
def create_budget():
    require_logged_in()
    require_fields(['name', 'interval'])

    name = request.form['name']
    interval = request.form['interval'].lower()

    if interval not in intervals_list:
        abort(400, 'Bad Request')
    
    interval_index = intervals_list.index(interval)

    isSuccess,result = get_db().create_budget(session['uid'], name, interval_index)
    if not isSuccess:
        return {}, 412
    else:
        return result

@blueprint.route('/api/list-budgets', methods=['GET'])
def list_budgets():
    require_logged_in()
    result = get_db().list_budgets(session['uid'])
    for i in range(len(result)):
        result[i]['interval'] = intervals_list[result[i]['interval']]
    return result

@blueprint.route('/api/get-budget', methods=['GET'])
def get_budgets():
    require_logged_in()
    require_args(['bid'])
    bid = request.args['bid']
    require_budget_access(bid, writeAccess=False)
    result = get_db().get_budget(bid)
    if 'interval' in result.keys():
        result['interval'] = intervals_list[result['interval']]
    return result

@blueprint.route('/api/update-budget-interval', methods=['POST'])
def update_budget():
    require_logged_in()
    require_fields(['bid', 'interval'])

    bid = request.form['bid']
    require_budget_access(bid, writeAccess=True)

    interval = request.form['interval']
    if interval not in ['month', 'trimester', 'semester', 'day', 'year']:
        abort(400, 'Bad Request')

    return get_db().update_budget_interval(bid, intervals_list.index(interval))

@blueprint.route('/api/create-income', methods=['POST'])
def create_income():
    require_logged_in()
    require_fields(['bid', 'name'])
    bid = int(request.form['bid'])
    name = request.form['name']
    if len(name) > 35:
        abort(400, 'Bad Request')
    
    require_budget_access(bid, writeAccess=True)

    return get_db().create_income(bid, name)

@blueprint.route('/api/create-expense', methods=['POST'])
def create_expense():
    require_logged_in()
    require_fields(['bid', 'name'])
    bid = int(request.form['bid'])
    name = request.form['name']
    if len(name) > 35:
        abort(400, 'Bad Request')
    
    require_budget_access(bid, writeAccess=True)

    return get_db().create_expense(bid, name)

@blueprint.route('/api/update-income', methods=['POST'])
def update_income():
    require_logged_in()
    require_fields(['bid', 'biid', 'field', 'value'])

    bid = int(request.form['bid'])
    biid = int(request.form['biid'])
    field = request.form['field']
    value = request.form['value']

    if field not in ['name', 'matcher', 'priority', 'safety_level']:
        abort(400, 'BadRequest')

    require_budget_access(bid, writeAccess=True)

    return get_db().update_income(bid, biid, field, value)

@blueprint.route('/api/update-expense', methods=['POST'])
def update_expense():
    require_logged_in()
    require_fields(['bid', 'bsid', 'field', 'value'])

    bid = int(request.form['bid'])
    bsid = int(request.form['bsid'])
    field = request.form['field']
    value = request.form['value']

    if field not in ['name', 'matcher', 'formula', 'priority']:
        abort(400, 'BadRequest')

    require_budget_access(bid, writeAccess=True)

    return get_db().update_expense(bid, bsid, field, value)

@blueprint.route('/api/delete-income', methods=['POST'])
def delete_income():
    require_logged_in()
    require_fields(['bid', 'biid'])

    bid = int(request.form['bid'])
    biid = int(request.form['biid'])

    require_budget_access(bid, writeAccess=True)

    return get_db().delete_income(bid, biid)


@blueprint.route('/api/delete-expense', methods=['POST'])
def delete_expense():
    require_logged_in()
    require_fields(['bid', 'bsid'])

    bid = int(request.form['bid'])
    bsid = int(request.form['bsid'])

    require_budget_access(bid, writeAccess=True)

    return get_db().delete_expense(bid, bsid)

@blueprint.route('/api/submit-contact', methods=['POST'])
def submit_contact():
    require_logged_in()
    require_fields(['first_name', 'last_name', 'email', 'country', 'content'])

    return get_db().submit_contact(session['uid'], request.form['first_name'], 
                                   request.form['last_name'], request.form['email'],
                                   request.form['country'], request.form['content'])