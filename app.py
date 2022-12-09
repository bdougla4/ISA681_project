from flask import escape, Flask, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import re
import bcrypt
import logging
from database.games import *
from database.users import *
from database.moves import *
#from game_play import *
# Loading .env file to keep database username/passwords from being hardcoded into source code.
from dotenv import load_dotenv
load_dotenv()

# Logging functionalilty for informational (and debugging).
logging.basicConfig(filename='app.log', filemode='a', encoding='utf-8', level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.urandom(12)

app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_USER'] = os.getenv('DB_SCRABBLE')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_SCRABBLE_PWD')
app.config['MYSQL_DB'] = os.getenv('DB_Scrabble')

# Connecting to MySQL database (MYSQL_DB)
db = MySQL(app)


app = Flask(__name__)
app.secret_key = os.urandom(12)

app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_USER'] = os.getenv('DB_SCRABBLE')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_SCRABBLE_PWD')
app.config['MYSQL_DB'] = os.getenv('DB_Scrabble')

# Connecting to MySQL database (MYSQL_DB)
db = MySQL(app)
# TO-DO: do we want to log things to a file?

# GLOBAL VARIABLES
attempts = 0  # logging number of password entry attempts for a user.

@app.route("/")
def homepage():
    """ISA Scrabble general homepage for users to Login, Register View Stats, and Play. """
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
        logging.info("Login request: %s" % (request.form["username"]))
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)

        # properly escaping user input to avoid XSS
        username = str(escape(request.form["username"]))
        password = escape(request.form["password"]).encode('utf-8')

        # check if username is in database
        cursor.execute("SELECT * from login where username='" + username + "'")
        account = cursor.fetchone()


        if account is None:
            msg = "No account with that name. Would you like to Register?"
            logging.info("Login request redirected to registration for %s" % escape(request.form["username"]))
            return render_template("index.html", msg=msg)
        else:
            # check if correct password was entered

            salt = account['salt'].encode('utf-8')
            enteredPswd = bcrypt.hashpw(password, salt)

            if enteredPswd == account['password'].encode('utf-8'):
                session['loggedin'] = True
                session['id'] = account['login_id']
                session['name'] = account['username']
                session['email'] = account['email']
                msg = "Welcome " + username + "!"
                logging.info("Logging sessionID: %s, user: %s, email: %s." % (session['id'], session['name'],
                                                                              session['email']))
                return render_template("user.html", msg=msg)
            else:
                msg = "Incorrect Username/Password!"
                logging.info("Invalid login attempt user: %s, email: %s." % (account['username'], account['email']))
                return render_template('login.html', msg=msg)
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    username = session['name']
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)

    # Redirect to login page
    return redirect(url_for('login'))


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
            elif not re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', escape(request.form['password'])):
                msg = 'Passwords must be a minimum of 8 characters, contain lower and upper case letters, numbers ' \
                      'and at least one special character (!, @, # $, ^, % *).'
            elif not username or not password or not email:
                msg = 'Please complete all required fields.'
            else:
                # generating salt and hashing password
                active = False
                salt = bcrypt.gensalt()
                password_hash = bcrypt.hashpw(password, salt)
                cursor.execute('INSERT INTO login (username, email, password, salt, actively_logged_in)'
                               'VALUES(%s, %s, %s, %s, %s)', (username, email, password_hash, salt, active))
                db.connection.commit()
                logging.info("Registering user: %s and updating database %s.login." % (username, app.config['MYSQL_DB']))
                msg = 'You have successfully registered! \nPlease login.'
                return render_template('index.html', msg=msg)
        elif request.method == 'POST':
            msg = 'Please complete all required fields.'
            logging.info("Registration failed for user. Not all fields completed.")
    elif request.method == 'POST':
        msg = 'Please complete all required fields.'
        logging.info("Registration failed for user. Not all fields completed.")
    return render_template('register.html', msg=msg)


if __name__ == "__main__":
    app.run()
