from flask import escape, Flask, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import re
import bcrypt

#Loding .env file to keep database username/passwords from being hardcoded into source code. 
from dotenv import load_dotenv
load_dotenv()
'''
from flaskext.mysql import MySQL
import mysql.connector
'''

app = Flask(__name__)
app.secret_key = os.urandom(12)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = os.getenv('DB_SCRABBLE')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_SCRABBLE_PWD')
app.config['MYSQL_DB'] = 'Login'

#Connecting to MySQL database (MYSQL_DB)
db = MySQL(app)


@app.route("/")
def homepage():
    """ISA Scrabble general homepage for users to Login database, Register or Reset password"""
    return render_template('index.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        #username = request.form["username"]
        # password = (request.form["password"]).encode('utf-8')

        #properly escaping user input to avoid XSS
        username = str(escape(request.form["username"]))
        password = escape(request.form["password"]).encode('utf-8')

        #check if username is in database
        cursor.execute("SELECT * from users where usrname='" + username + "'")
        account = cursor.fetchone()

        ## cursor.execute("SELECT * from users where usrname='" + username + "' and password='" + password + "'")

        if account is None:
            msg = "No account with that name. Would you like to Register?"
            print("msg " + msg)
            return render_template("index.html", msg=msg)
        else:
            #check if correct password was entered
            salt = account['salt'].encode('utf-8')
            enteredPswd = bcrypt.hashpw(password, salt)

            if enteredPswd == account['passwordHash'].encode('utf-8'):
                session['loggedin'] = True
                session['id'] = account['userID']
                session['name'] = account['usrname']
                session['email'] = account['email']
                msg = "Welcome " + username + "!"
                return render_template("user.html", msg=msg)
            else:
                msg = "Incorrect Username/Password!"
                return render_template('login.html', msg=msg)
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)

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
            cursor.execute('SELECT * FROM users WHERE usrname = %s', (username,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists !'
                return render_template('login.html', msg=msg)
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not username or not password or not email:
                msg = 'Please complete all required fields.'
            else:
                #generating salt and hashing password
                salt = bcrypt.gensalt()
                passwordHash = bcrypt.hashpw(password, salt)
                cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s, %s)', (username, passwordHash, salt, email,))
                db.connection.commit()
                msg = 'You have successfully registered !'
        elif request.method == 'POST':
            msg = 'Please complete all required fields.'
    elif request.method == 'POST':
        msg = 'Please complete all required fields.'
    return render_template('register.html', msg=msg)


if __name__ == "__main__":
    app.run()
