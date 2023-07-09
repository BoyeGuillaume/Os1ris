from flask import Flask, request, session, render_template, abort, redirect, url_for, g
from markupsafe import escape
from secrets import token_bytes
from utils import DatabaseHandle
import sqlite3
from api import blueprint
from waitress import serve

app = Flask(__name__, static_url_path='/static')
app.secret_key = token_bytes(32)
app.register_blueprint(blueprint)

# WARNING : EVERYONE IS EVERYONE
@app.before_request
def initialize():
    session['uid'] = 1

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
    return DatabaseHandle(db)

def init_db():
    with app.app_context():
        db = get_db().db
        with app.open_resource('shema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
@app.route("/index")
@app.route("/index/<path:subpath>")
def index(**kwargs):
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        # return app.send_static_file('index.html')
        return redirect('/login')

@app.route("/login", methods = ["GET", "POST"])
@app.route("/signup", methods = ["GET", "POST"])
def login_or_signup_get():
    error = None

    # If already logged in, skip this page and redirect directly to the index
    if request.path == '/login':
        if 'username' in session:
            return redirect('/index')
    
        if request.method == 'POST':
            isValid, uid = get_db().is_valid_user(request.form['username'], request.form['password'])
            if isValid:
                session['username'] = request.form['username']
                session['uid'] = uid
                return redirect('/index')
            error = 'Invalid credential'

    elif request.path == '/signup':
        if request.method == 'POST':
            if request.form['password'] != request.form['confirm-password']:
                error = 'Both password must match'
            elif len(request.form['password']) < 5:
                error = 'Password is to short, requires at least 5 characters'
            else:
                isValid, uid = get_db().register_user(request.form['username'], request.form['password'])
                if isValid:
                    session['username'] = request.form['username']
                    session['uid'] = uid
                    return redirect('/index')
                error = 'Username already in use'

    # The code below is executed if the request method
    # was GET or the credential were invalid
    return render_template('login_or_signup.html', error=error, login=(request.path == '/login'))

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect('/index')

@app.route("/favicon.svg")
def favicon():
    return app.send_static_file("logo/svg/favicon.svg")

@app.route("/user-profile-icon.png")
def user_logo():
    return app.send_static_file("user-logo.png")

if __name__ == '__main__':
    serve(app, host='127.0.0.1', port=80, url_scheme='https')
