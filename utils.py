import sqlite3
import hashlib
import hmac
import sqlite3
import os
import json
import datetime
import re
from flask import abort
from query import sanitize_safe_sql_filter, sanitize_safe_sql_value, evaluate
from math import floor
import time

intervals_list = ['day', 'month', 'trimester', 'semester', 'year']

def require_date(string):
    if not re.fullmatch(r'^\d*-\d\d?-\d\d?', string):
        abort(400, 'Bad Request')

default_safe_identifier = [
    'id',
    'account',
    'date',
    'available_date',
    'registration_date',
    'amount',
    'description',
    'tags'
]

def sanitize_or_empty(code, filter = False, safe_identifier=[]):
    if len(code.strip()) == 0:
        return ''
    else:
        if filter:
            return sanitize_safe_sql_filter(code, safe_identifier=safe_identifier)
        else:
            return sanitize_safe_sql_value(code, safe_identifier=safe_identifier)

def date_time_interval_format(interval, date_name):
    def partition(initial, interval):
        return f'(CAST(ROUND(0.4999 + CAST({initial} AS REAL) / {interval}) AS INT) * {interval})'

    if interval == 'day':
        group_by_format = f"strftime('%Y-%m-%d', {date_name})"
    elif interval == 'month':
        group_by_format = f"strftime('%Y-%m', {date_name})"
    elif interval == 'trimester':
        group_by_format = f"strftime('%Y', {date_name}) || '-' || " + partition(f"strftime('%m', {date_name})", 4)
    elif interval == 'semester':
        group_by_format = f"strftime('%Y', {date_name}) || '-' || " + partition(f"strftime('%m', {date_name})", 6)
    elif interval == 'year':
        group_by_format = f"strftime('%Y', {date_name})"
    else:
        abort(400, 'Bad Request')
    return group_by_format


class DatabaseHandle:
    def __init__(self, db : sqlite3.Connection):
        self.db : sqlite3.Connection = db
        self.db.row_factory = sqlite3.Row

    def __get_cursor(self) -> sqlite3.Cursor:
        return self.db.cursor()

    def is_valid_user(self, username: str, password: str) -> bool:
        # Perform the database request
        cur = self.__get_cursor()
        res = cur.execute("SELECT uid, password_hash, salt FROM Users WHERE username = ?", (username,))
        result = res.fetchone()
        if result is None:
            return (False, None)
        uid, password_hash, salt = result
        cur.close()

        # Compare the logins with the database
        return hmac.compare_digest(
            password_hash,
            hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        ), uid
    
    def create_account(self, uid, name, creation_date, currency, description):
        try:
            try:
                datetime.datetime.strptime(creation_date, "%Y-%m-%d")
            except ValueError:
                return (False, None)

            cur = self.__get_cursor()
            cur.execute('begin')
            
            cur.execute('SELECT * FROM Accounts WHERE uid = ? AND name = ?', (uid, name,))
            if len(cur.fetchall()) > 0:
                return (False, None)

            cur.execute('INSERT INTO Accounts (uid, creation_date, registration_date, currency, name, description) VALUES (?, ?, DATETIME(), ?, ?, ?)', (uid, creation_date, currency, name, description))
            aid = cur.lastrowid

            cur.execute('commit')
            cur.close()
            
            return (True, aid)
        except sqlite3.IntegrityError as e:
            return (False, None)
    
    def delete_account(self, aid):
        cur = self.__get_cursor()
    
        cur.execute('DELETE FROM TransactionHasTag WHERE tid IN (SELECT id FROM Transactions WHERE account = ?)', (aid,))
        cur.execute('DELETE FROM Transactions WHERE account = ?', (aid,))
        cur.execute('DELETE FROM Accounts WHERE aid = ?', (aid,))

        cur.execute('commit')
        cur.close()

        return {}

    def register_user(self, username: str, password: str):
        if len(username.strip()) == 0:
            return (False, None)
        
        try:
            # Generate the salt
            salt = os.urandom(16)
            pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)

            # Try to add the element into the database
            cur = self.__get_cursor()
            cur.execute('INSERT INTO Users (username, password_hash, salt, registration_date) VALUES (?, ?, ?, DATETIME())', (username, pw_hash, salt))
            self.db.commit()

            # Fetch the newly UID
            cur.execute('SELECT uid FROM Users WHERE username = ?', (username,))
            uid, = cur.fetchone()
            cur.close()
            return (True, uid)
        except sqlite3.IntegrityError as e:
            return (False, None)
        
    def has_access(self, uid, aid, ownership):
        cur = self.__get_cursor()
        res = cur.execute('SELECT 1 FROM Accounts WHERE aid = ? AND uid = ?', (aid,uid,))
        res = res.fetchone()
        cur.close()
        return res != None

    def has_budget_access(self, uid, bid, ownership):
        cur = self.__get_cursor()
        cur.execute('SELECT 1 FROM Budget WHERE bid = ? AND uid = ?', (bid,uid,))
        result = cur.fetchone() != None
        cur.close()
        return result

    def list_account(self, uid):
        
        # Find all accounts own by the specified user
        cur = self.__get_cursor()
        cur.execute('SELECT aid, creation_date, currency, name, description FROM Accounts A WHERE A.uid = ?', (uid,))
        res = cur.fetchall()
        cur.close()

        return [dict(i) for i in res]
    
    def get_account(self, aid):
        cur = self.__get_cursor()
        cur.execute('SELECT * FROM Accounts A WHERE A.aid = ?', (aid,))
        res = cur.fetchone()
        cur.close()
        res = dict(res)

        cur = self.__get_cursor()
        cur.execute('SELECT COUNT(DISTINCT id) FROM Transactions WHERE account = ?', (aid,))
        res['number_of_transaction'] = cur.fetchone()[0]
        cur.close()

        return res

    def list_tags(self, uid, cur_ = None):
        if cur_:
            cur = cur_
        else:
            cur = self.__get_cursor() 

        cur.execute('SELECT id, name, description, color FROM Tags WHERE uid = ?', (uid,))
        res = cur.fetchall()
        
        if not cur_:
            cur.close()
        
        return [dict(i) for i in res]

    def create_transaction(self, uid, aid, amount, date, available_date, description, tags = []):
        require_date(date)
        if available_date != '':
            require_date(available_date)
        cur = self.__get_cursor()
        cur.execute('begin')

        tags_list = self.list_tags(uid, cur)

        try:
            # Retrieve information about the account
            cur.execute('UPDATE Accounts SET last_transaction_date = DATETIME() WHERE aid = ?', (aid,))

            # Add the transaction
            cur.execute('INSERT INTO Transactions (account, uid, date, available_date, registration_date, amount, description) VALUES (?, ?, ?, ?, DATETIME(), ?, ?)', (aid, uid, date, available_date, amount, description,))

            # For each tag, add corresponding tag to transaction
            transaction_id = cur.lastrowid
            for tag in list(set(tags)):
                # Attempt to find the tag within tag list
                id = None
                for tg in tags_list:
                    if tg['name'] == tag:
                        id = tg['id']
                        break
            
                if not id:
                    cur.execute('INSERT INTO Tags (uid, name) VALUES (?, ?)', (uid, tag,))
                    id = cur.lastrowid
                
                # Insert the tag in TransactionHasTag
                cur.execute('INSERT INTO TransactionHasTag (tid, tag) VALUES (?, ?)', (transaction_id,id,))

            cur.execute('commit')
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print('Error: {}'.format(e))
            cur.execute('rollback')
            return False


    def get_transaction(self, uid, aid, offset, limit, search = None, sort = None):
        res = {}

        cur = self.__get_cursor()
        prefix_string = "WITH NamedTransactionHasTag AS ( SELECT TransactionHasTag.*, Tags.name FROM TransactionHasTag, Tags WHERE TransactionHasTag.tag = Tags.id ) "
        request_string = \
            "SELECT Transactions.*, COALESCE(GROUP_CONCAT(T.tag, ','), '') as tags " + \
            "FROM TRANSACTIONS " + \
            "LEFT JOIN NamedTransactionHasTag T ON T.tid = id " + \
            "GROUP BY id " + \
            "HAVING account = ? "
        request_tuple = (aid,)
        search_postfix = ''

        if search:
            search_postfix = "AND (description LIKE '%'||?||'%' OR date LIKE '%'||?||'%' OR available_date LIKE '%'||?||'%' OR registration_date LIKE '%'||?||'%' OR amount LIKE '%'||?||'%' OR GROUP_CONCAT(T.name, ',') LIKE '%'||?||'%' ) "
            request_string += search_postfix
            request_tuple = sum((request_tuple, (search,search,search,search,search,search)), ())

        cur.execute(f'{prefix_string} SELECT COUNT(*) FROM ({request_string})', request_tuple)
        res['count'] = cur.fetchone()[0]

        if sort:
            keyword, dir = sort

            # These checks below are to ensure no SQL injection is possible
            if dir.lower() not in ['asc', 'desc']:
                abort(400, 'dir must but in [asc, desc]')
            if keyword not in ['id', 'date', 'available_date', 'registration_date', 'amount']:
                abort(400, 'keyword not recognised')

            request_string += f'ORDER BY {keyword.lower()} {dir.upper()} ' # Beware of SQL injection !!
        
        if offset != None and limit != None:
            request_string += 'LIMIT ? OFFSET ? '
            request_tuple = sum((request_tuple, (limit, offset,)), ())

        res['results'] = [dict(i) for i in cur.execute(prefix_string + request_string, request_tuple).fetchall()]
        res['tags'] = self.list_tags(uid, cur)

        cur.close()

        return res
    
    def get_balance(self, aid):
        cur = self.__get_cursor()
        cur.execute('SELECT COALESCE(SUM(amount), 0) AS balance FROM Transactions WHERE account = ?', (aid,))
        res = {
            'balance': cur.fetchone()['balance']
        }
        
        r = cur.execute('SELECT COALESCE(SUM(amount), 0) AS available_balance FROM Transactions WHERE account = ? AND available_date IS NOT NULL AND available_date != ""', (aid,))
        res['available_balance'] = r.fetchone()['available_balance']
        cur.close()
        return res
    
    def get_history(self, aid, interval, date_type):

        if date_type not in ['date', 'available_date']:
            abort(500, 'Internal Server Error')

        group_by_format = date_time_interval_format(interval, date_type)
        
        cur = self.__get_cursor()
        cur.execute(f'SELECT {group_by_format} AS {date_type}, SUM(amount) AS balance FROM Transactions WHERE account = ?' + \
                    f'GROUP BY {group_by_format} ORDER BY {group_by_format} DESC', (aid,))
        results = cur.fetchall()
        cur.close()

        return [dict(i) for i in results]

    def update_tag(self, uid, id, name, color):
        cur = self.__get_cursor()
        cur.execute('SELECT uid FROM Tags WHERE id = ?', (id,))
        if uid != cur.fetchone()['uid']:
            abort(403, 'Forbidden')
        cur.execute('UPDATE Tags SET name = ?, color = ? WHERE id = ?', (name,color,id,))
        cur.execute('commit')
        cur.close()
        return {}
    
    def delete_transaction(self, aid, id):
        cur = self.__get_cursor()
        cur.execute('SELECT id FROM Transactions WHERE account = ? and id = ?', (aid, id,))
        for row in cur.fetchall():
            cur.execute('DELETE FROM TransactionHasTag WHERE tid = ?', (row['id'],))
        cur.execute('DELETE FROM Transactions WHERE account = ? and id = ?', (aid, id,))
        cur.execute('commit')
        cur.close()
        return {}
    
    def update_transaction(self, aid, id, field, value):
        cur = self.__get_cursor()
        if field == 'date':
            require_date(value)
        if field == 'available_date':
            if value == '':
                value = None
            else:
                require_date(value)
        cur.execute('SELECT account FROM Transactions WHERE id = ?', (id,))
        if aid != cur.fetchone()['account']:
            abort(403, 'Forbidden')
        cur.execute(f'UPDATE Transactions SET {field} = ? WHERE account = ? AND id = ?', (value,aid,id))
        cur.execute('commit')
        cur.close()
        return {}
    
    def create_budget(self, uid, name, interval_index):
        cur = self.__get_cursor()
        cur.execute('begin')

        cur.execute('SELECT * FROM Budget WHERE uid = ? AND name = ?', (uid, name,))
        if len(cur.fetchall()) > 0:
            return (False, None)

        cur.execute('INSERT INTO Budget (uid, name, interval) VALUES (?, ?, ?)', (uid, name, interval_index))
        bid = cur.lastrowid

        cur.execute('commit')
        cur.close()

        return (True, { 'bid': bid })
    
    def update_budget_interval(self, bid, interval_index):
        cur = self.__get_cursor()

        cur.execute('UPDATE Budget SET interval = ? WHERE bid = ?', (interval_index, bid,))
        cur.execute('commit')
        cur.close()

        return {}
        
    
    def create_income(self, bid, name):
        cur = self.__get_cursor()

        cur.execute('INSERT INTO BudgetIncomeCategory (bid, name, matcher, priority, safety_level) VALUES (?, ?, "", 999, 1.0)', (bid,name,))
        cur.execute('commit')

        cur.close()
        return {}
    
    def create_expense(self, bid, name):
        cur = self.__get_cursor()

        cur.execute('INSERT INTO BudgetSpendingCategory (bid, name, matcher, formula, priority) VALUES (?, ?, "", "", 999)', (bid,name,))
        cur.execute('commit')

        cur.close()
        return {}
    
    def update_income(self, bid, biid, field, value):
        assert field in ['name', 'matcher', 'priority', 'safety_level']
        start = time.time_ns()

        cur = self.__get_cursor()
        
        if field == 'matcher': # Need to sanitize sql code to prevent injection
            try:
                sanitize_or_empty(value, filter=(field == 'matcher'), safe_identifier=default_safe_identifier)
            except Exception as e:
                print(e)
                return { 'Error': f'Not acceptable: Failed to compile matcher/level - "{e}"' }
            
        if field == 'safety_level':
            if float(value) < 0.0 or float(value) > 1.0:
                return { 'Error': f'Not acceptable: safety_level should be a value between 0 and 1' }
        
        if field != 'name': # Need to sanitize sql code to prevent injection
            try:
                sanitize_or_empty(value, filter=(field == 'matcher'), safe_identifier=default_safe_identifier)
            except Exception as e:
                return { 'Error': f'Not acceptable: Failed to compile matcher/level - "{e}"' }

        elapsed = time.time_ns() - start

        cur.execute(f'UPDATE BudgetIncomeCategory SET {field} = ? WHERE bid = ? AND biid = ?', (value, bid, biid,))
        cur.execute('commit')
        
        cur.close()

        if field == 'matcher':
            return { 'Message': f'Query successfully compiled in {(elapsed // 100000) / 10.0} ms' }
        elif field == 'name':
            return { 'Message': 'Name successfully updated' }
        elif field == 'priority':
            return { 'Message': 'Priority successfully updated' }
        elif field == 'safety_level':
            return { 'Message': 'Safety Level successfully updated' }
    
    def update_expense(self, bid, bsid, field, value):
        assert field in ['name', 'matcher', 'formula', 'priority']
        start = time.time_ns()

        cur = self.__get_cursor()
        
        if field not in ['name', 'priority']: # Need to sanitize sql code to prevent injection
            try:
                sanitize_or_empty(value, filter=(field == 'matcher'), safe_identifier=default_safe_identifier)
            except Exception as e:
                print(e)
                return { 'Error': f'Not acceptable: Failed to compile matcher/level - "{e}"' }
            
        elapsed = time.time_ns() - start

        cur.execute(f'UPDATE BudgetSpendingCategory SET {field} = ? WHERE bid = ? AND bsid = ?', (value, bid, bsid,))
        cur.execute('commit')
        
        cur.close()

        if field in ['formula', 'matcher']:
            return { 'Message': f'Query successfully compiled in {(elapsed // 100000) / 10.0} ms' }
        elif field == 'name':
            return { 'Message': 'Name successfully updated' }
        elif field == 'priority':
            return { 'Message': 'Priority successfully updated' }

    def list_budgets(self, uid):
        cur = self.__get_cursor()
        cur.execute('SELECT bid, name, interval FROM Budget WHERE uid = ?', (uid,))
        return [dict(x) for x in cur.fetchall()]
    
    def compute_budget(self, uid, bid, interval, cur_ = None):
        cur = cur_
        if not cur:
            cur = self.__get_cursor()

        query = \
            'WITH NamedTransactionHasTag ' +\
            ' AS ( '+\
                'SELECT TransactionHasTag.*, Tags.name '+\
                'FROM TransactionHasTag, Tags '+\
                'WHERE TransactionHasTag.tag = Tags.id'+\
            ' ), ' +\
            ' available_transaction AS ('+\
                'SELECT Transactions.id, A.name as account, Transactions.date, Transactions.available_date, Transactions.registration_date, Transactions.amount, Transactions.description, COALESCE(GROUP_CONCAT(T.name, \',\'), \'\') as tags '+\
                'FROM Transactions '+\
                'LEFT JOIN Accounts A ON A.uid = account '+\
                'LEFT JOIN NamedTransactionHasTag T ON T.tid = id '+\
                'GROUP BY id HAVING Transactions.uid = ?'+\
            ' ) ' +\
            'SELECT COALESCE(GROUP_CONCAT(id, \',\'), \'\') as ids, COUNT(id) as count, '+ date_time_interval_format(intervals_list[interval], 'date') + ' as date, SUM(amount) as amount FROM available_transaction WHERE {} AND ({})' +\
            'GROUP BY ' + date_time_interval_format(intervals_list[interval], 'date')

        cur.execute('SELECT * FROM Budget, BudgetIncomeCategory '+\
                    'WHERE BudgetIncomeCategory.bid = Budget.bid AND Budget.bid = ? ORDER BY priority ASC', bid)

        incomes = []

        # For each income source, retrieve
        # matching columns
        incomes_ids = set()
        total_income = 0.0
        raw_income = 0.0
    
        for income in cur.fetchall():
            matcher = income['matcher']
            if matcher == '':
                continue

            try:
                r = cur.execute(query.format('amount > 0.0 AND id NOT IN ({})'.format(','.join([str(i) for i in incomes_ids])), income['matcher']), (uid,))
                raw_result = []
                partial_result = []
                for row in r.fetchall():
                    total_amount = floor((1.0 - income['safety_level']) * float(row['amount']) * 100.0) / 100.0
                    for i in row['ids'].split(','):
                        incomes_ids.add(i)
                    partial_result.append({
                        'date': row['date'],
                        'raw_income': row['amount'],
                        'income': total_amount,
                        'count': row['count']
                    })

                    total_income += total_amount
                    raw_income += row['amount']

                incomes.append({
                    'biid': income['biid'],
                    'list': partial_result,
                    'total_income': total_income,
                    'raw_income': raw_income
                })
                # total_income += total_amount
                # raw_income += r['amount']
            except sqlite3.OperationalError as e:
                incomes.append({
                    'biid': income['biid'],
                    'error': str(e)
                })

            
        cur.execute('SELECT * FROM Budget, BudgetSpendingCategory '+\
                    'WHERE BudgetSpendingCategory.bid = Budget.bid AND Budget.bid = ? ORDER BY priority ASC', bid)

        expenses = []

        # For each outcome source, retrieve
        # matching columns
        expenses_ids = set()

        for expense in list(cur.fetchall()):
            matcher, value = expense['matcher'], expense['formula']
            if matcher == '' or value == '':
                continue
            try:
                r = cur.execute(query.format('amount > 0.0 AND id NOT IN ({})'.format(','.join([str(i) for i in incomes_ids])), income['matcher']), (uid,))
                for row in r.fetchall():
                    for i in row['ids'].split(','):
                        incomes_ids.add(i)

                expenses.append({
                    'bsid': expense['bsid'],
                    # 'count': r['count'],
                    # 'used': r['amount'],
                    # 'ids': r['ids'],
                })
            except sqlite3.OperationalError as e:
                expenses.append({
                    'bsid': expense['bsid'],
                    'error': str(e)
                })
        
        res = {
            'incomes': incomes,
            'expenses': expenses
        }

        if not cur_:
            cur.close()
        return res

    def get_budget(self, bid):
        cur = self.__get_cursor()

        cur.execute('SELECT uid, bid, interval, name FROM Budget WHERE bid = ?', (bid,))
        res = dict(cur.fetchone())

        cur.execute('SELECT * FROM BudgetSpendingCategory WHERE bid = ? ORDER BY priority ASC', (bid,))
        res['expense'] = [dict(x) for x in cur.fetchall()]


        cur.execute('SELECT * FROM BudgetIncomeCategory WHERE bid = ? ORDER BY priority ASC', (bid,))
        res['income'] = [dict(x) for x in cur.fetchall()]
        res['result'] = self.compute_budget(int(res['uid']), bid, res['interval'], cur_=cur)
        
        cur.close()
        
        return res
    
    def delete_income(self, bid, biid):
        cur = self.__get_cursor()
        cur.execute(f'DELETE FROM BudgetIncomeCategory WHERE bid = ? AND biid = ?', (bid, biid,))
        cur.execute('commit')
        cur.close()
        return {}
    
    def delete_expense(self, bid, bsid):
        cur = self.__get_cursor()
        cur.execute(f'DELETE FROM BudgetSpendingCategory WHERE bid = ? AND bsid = ?', (bid, bsid,))
        cur.execute('commit')
        cur.close()
        return {}

    def submit_contact(self, uid, first_name, last_name, email, country, content):
        cur = self.__get_cursor()
        cur.execute('INSERT INTO Ticket (uid, date, name, last_name, email, country, content) VALUES (?, DATETIME(), ?, ?, ?, ?, ?)', (uid, first_name, last_name, email, country, content,))
        cur.execute('commit')
        cur.close()
        return {}

    def to_json(self, result):
        return json.dumps([dict(i) for i in result])
    
    def to_json2(self, result):
        return json.dumps(dict(result))