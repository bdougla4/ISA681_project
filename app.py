from flask import escape, Flask, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import re
import bcrypt
import datetime as dt

# Loading .env file to keep database username/passwords from being hardcoded into source code.
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(12)

app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_USER'] = os.getenv('DB_SCRABBLE')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_SCRABBLE_PWD')
app.config['MYSQL_DB'] = os.getenv('DB_Scrabble')

# Connecting to MySQL database (MYSQL_DB)
db = MySQL(app)


@app.route("/")
def homepage():
    """ISA Scrabble general homepage for users to Login database, Register or Reset password"""
    return render_template('index.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    """
    Login route to check username and password in the database. If user is already logged in, users
    are redirected to their user profile where they are able to continue any previous games, or start a new one.
    Function takes user input from the login.html form, escapes the contents and compares the provided credentials with
    the stored information in the database.
    """

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)

        # properly escaping user input to avoid XSS
        username = str(escape(request.form["username"]))
        password = escape(request.form["password"]).encode('utf-8')

        # check if username is in database
        cursor.execute("SELECT * from login where username='" + username + "'")
        account = cursor.fetchone()

        if account is None:
            msg = "No account with that name. Would you like to Register?"
            print("msg " + msg)
            return render_template("index.html", msg=msg)
        else:
            # check if correct password was entered
            salt = account['salt'].encode('utf-8')
            entered_pswd = bcrypt.hashpw(password, salt)

            if entered_pswd == account['password'].encode('utf-8'):
                session['loggedin'] = True
                session['id'] = account['login_id']
                session['name'] = account['username']
                session['email'] = account['email']
                session['login_time'] = dt.datetime.now()
                cursor.execute('UPDATE login SET actively_logged_in=%s WHERE username=%s',
                               (True, username))
                db.connection.commit()
                msg = "Welcome " + username + "!"
                return render_template("user.html", msg=msg)
            else:
                msg = "Incorrect Username/Password!"
                return render_template('login.html', msg=msg)
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    username = session['name']
    session.pop('actively_logged_in', None)
    session.pop('id', None)
    session.pop('name', None)

    # Updating database to log user out and update logged_out timestamp
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE login SET actively_logged_in=%s WHERE username=%s',
                   (False, username))
    db.connection.commit()

    # Redirect to login page
    return redirect(url_for('login'))


@app.route('/reset', methods=['POST'])
def reset():
    msg = ''
    return render_template('register.html', msg=msg)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        if 'email' in request.form:
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            username = escape(request.form['username'])
            password = escape(request.form['password']).encode('utf-8')
            email = escape(request.form['email'])
            cursor.execute('SELECT * FROM login WHERE username = %s', (username,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists !'
                return render_template('login.html', msg=msg)
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not username or not password or not email:
                msg = 'Please complete all required fields.'
            else:
                # generating salt and hashing password
                salt = bcrypt.gensalt()
                password_hash = bcrypt.hashpw(password, salt)
                # registered = ((dt.datetime.now()).strftime('%Y-%m-%d %H:%M:%S'))
                active = False
                cursor.execute('INSERT INTO login (username, email, password, salt, actively_logged_in) '
                               'VALUES(%s, %s, %s, %s, %s)', (username, email, password_hash, salt, active))
                db.connection.commit()
                msg = 'You have successfully registered! \nPlease login.'
                return render_template('index.html', msg=msg)
        elif request.method == 'POST':
            msg = 'Please complete all required fields.'
    elif request.method == 'POST':
        msg = 'Please complete all required fields.'
    return render_template('register.html', msg=msg)


if __name__ == "__main__":
    app.run()
