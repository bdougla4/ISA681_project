from flask import escape, Flask, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import re
import bcrypt
import logging
from database.games import *
#Loding .env file to keep database username/passwords from being hardcoded into source code. 
from dotenv import load_dotenv
load_dotenv()
'''
from flaskext.mysql import MySQL
import mysql.connector
'''

app = Flask(__name__)
app.secret_key = os.urandom(12)

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'scrabble'

#Connecting to MySQL database (MYSQL_DB)
db = MySQL(app)
# TO-DO: do we want to log things to a file? 
logging.basicConfig(level=logging.DEBUG)


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


@app.route('/board/', methods=['GET', 'POST'])
def board():
    return render_template('board.html')

@app.route('/menu/', methods=['GET', 'POST'])
def menu():
    username = 364952648
    activeGame = False
    logging.info("checking if user has active game")
    dbCur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    if Games.get_all_active_games_for_single_user_id(dbCur, username) != None:
        activeGame = True 
        logging.info("user has active game")

    logging.info("active game = %s", activeGame)
    return render_template('menu.html', activeGame=activeGame, gameForfeited=False)

@app.route('/end-game/', methods=['GET', 'POST'])
def forfeitGame():
    username = 364952648
    username2 = 1356773521
    dbCur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    logging.info("user: %s forfeited game", username)

    # TO-DO get the correct username to mark as winner
    Games.game_finished(Games, dbCur, username, username2, username2)
    db.connection.commit()
    return render_template('menu.html', activeGame=False, gameForfeited=True)

@app.route('/scoreboard/', methods=['GET', 'POST'])
def scoreboard():
    print(request.args)
    if request.method == 'GET' and (('username' in request.args) or 
    ('user-score' in request.args) or ('self-score' in request.args)):
        # print(request.args)
        
        # str(escape(request.form["username"]))
        # elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        # pattern="[A-Za-z]{50} | [^@]+@[^@]+\.[^@]+">
        username = request.args.get('username')
        print('username: ')
        print(username)
        if (username != ''):
            username = str(escape(username))
            if ((re.match(r'[^@]+@[^@]+\.[^@]+', username)) or (re.match(r'[A-Za-z]{1,50}', username))):
                print('good username format')
            else:
                print('bad username format')
        # print('username: ')
        # print(username)
        # if user requests to see another user's score:
        userScore = request.args.get('user-score')
        # if user requests to see their own scores:
        selfScore = request.args.get('self-score')            



    return render_template('scoreboard.html')

# @app.route('/scores/', methods=['GET', 'POST'])
# def scores():
#     print('in scores')
#     print(request.form['user-score'])    
#     print(request.form['self-score'])
#     # return render_template('score-board.html')

        


if __name__ == "__main__":
    app.run()
