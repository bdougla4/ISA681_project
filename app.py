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
from game_play import *
#Loding .env file to keep database username/passwords from being hardcoded into source code. 
from dotenv import load_dotenv
load_dotenv()
'''
from flaskext.mysql import MySQL
import mysql.connector
'''

userid = '364952648'
userid2 = '1356773521'

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

@app.route('/menu/', methods=['GET', 'POST'])
def menu():
    activeGame = False
    logging.debug("checking if user has active game")
    dbCur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    if Games.get_all_active_games_for_single_user_id(dbCur, userid) != None:
        activeGame = True 
        logging.info("user has active game")

    logging.info("active game = %s", activeGame)
    return render_template('menu.html', activeGame=activeGame, gameForfeited=False)

@app.route('/game/', methods=['GET', 'POST'])
def game():
    displayUndefinedError = None
    displayForfeitError = None
    playerStats = None
    try:
        dbCur = db.connection.cursor(MySQLdb.cursors.DictCursor)
        # used in the case that a user enters a non defined word and old stats need to stay on board
        if ('gameStatus' in request.args):
            gameStatus = request.args.get('gameStatus')
            if gameStatus == 'continue':
                logging.debug("user wants to continue previous game. checking if user has active game")
                # TO-DO: get user id
                currentGame = Games.get_all_active_games_for_single_user_id(dbCur, userid)
                if currentGame != None:
                    logging.info("user has active game")
                    currentUsersTurn = currentGame['current_users_turn']
                    playerStats = GamePlay.generate_continue_game_stats(dbCur, currentGame)
                else:
                    raise UserForfeitedException("Other user forfeited during game play")
        if ('submit-user-input' in request.form and 'user-word' in request.form and 
        'user-position' in request.form and 'col' in request.form and 'row' in request.form):
            logging.debug('user submitted position, word, row, and column')
            position = str(escape(request.form["user-position"]))
            word = str(escape(request.form["user-word"]))
            col = str(escape(request.form["col"]))
            row = str(escape(request.form["row"]))
            # TO-DO: make sure it is user's turn when inserting move
            # TO-DO: get user id
            playerStats = GamePlay.handle_users_input(GamePlay, dbCur, currentGame['game_id'], currentUsersTurn, word, position, col, row)
            db.connection.commit()
    except UserForfeitedException as err:
        logging.warning("Other user forfeited during game play. Displaying error to UI")
        displayForfeitError = True
    except UndefinedWordException as err:
        logging.warning("User's input was invalid. Displaying error to UI")
        displayUndefinedError = True

            
    return render_template('game.html', gameStatus='continue', playerStats=playerStats, 
        displayUndefinedError=displayUndefinedError, displayForfeitError=displayForfeitError)

@app.route('/new-game/', methods=['GET', 'POST'])
def newGame():
    # TO-DO: get userid from actual user
    dbCur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    logging.debug("user: %s is requesting to join new game", userid)

    logging.debug("Making sure user does not have an active game already")
    # TO-DO get the correct userid to check for active games
    activeGames = Games.get_all_active_games_for_single_user_id(dbCur, userid)

    if activeGames != None:
        logging.warn('User: %s is requesting a new game but already has an active one running', userid)
    else:
        logging.debug('User has no active games currently. Creating a new game')
        # TO-DO: how to get a second user to join this game?
        # TO-DO get the correct userids
        gameId = Games.add_game(dbCur, userid, userid2)
        db.connection.commit()

        newGame = Games.get_game_by_id(dbCur, gameId)
        playerStats = GamePlay.generate_new_game_stats(dbCur, newGame)
        return render_template('game.html', gameStatus='newGame', playerStats=playerStats)
    

@app.route('/end-game/', methods=['GET', 'POST'])
def forfeitGame():
    # TO-DO: get userid from actual user
    dbCur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    logging.info("user: %s forfeited game", userid)

    # TO-DO get the correct userid to mark as winner
    Games.game_finished(Games, dbCur, userid, userid2, userid2)

    # TO-DO get the correct userid to mark as winner
    Users.set_user_lost(Users, dbCur, userid)

    # TO-DO get the correct userid to mark as winner
    Users.set_user_won(Users, dbCur, userid2)

    db.connection.commit()
    return render_template('menu.html', activeGame=False, gameForfeited=True)

@app.route('/scoreboard/', methods=['GET', 'POST'])
def scoreboard():
    userScore = request.args.get('user-score')
    if request.method == 'GET' and (('username' in request.args) or 
    ('user-score' in request.args) or ('self-score' in request.args)):
        if((userScore == None) or (userScore == '')):
            username = 'user1'
            logging.debug('user: %s wants to see their own personal scores', username)
            return generateScoreboard(username)

        username = request.args.get('username')
        if (username != ''):
            username = str(escape(username))
            logging.info('user is requesting score for user: %s', username)
            # if ((re.match(r'[^@]+@[^@]+\.[^@]+', username)) or (re.match(r'[A-Za-z]{1,50}', username))):

            if re.match(r'[A-Za-z0-9]{1,50}', username):
                logging.info('%s is good username format', username)
                # userScore = request.args.get('user-score')     
                return generateScoreboard(username)
            else:
                logging.warn('%s is bad username format', username)
  
    return render_template('scoreboard.html')

def generateScoreboard(username):
    noScores = False
    userFinalScores = None
    dbCur = db.connection.cursor(MySQLdb.cursors.DictCursor)

    logging.debug('getting score for user: %s', username)
    # TO-DO: get username for current user
    scoresRetrieved = Users.get_user_score_board(Users, dbCur, username)
    if scoresRetrieved != []:
        # TO-DO: get username for current user
        userFinalScores = Users.get_user_by_user_name(Users, dbCur, username)
    else:
        noScores = True

    return render_template('scoreboard.html', scoresRetrieved=scoresRetrieved, username=username, userFinalScores=userFinalScores, noScores=noScores) 


@app.route('/moves/', methods=['GET', 'POST'])
def getMoves():
    gameId = request.args.get('gameId')
    logging.debug('getting moves for gameId: %s', gameId)

    dbCur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    gameMoves = Moves.get_all_moves_for_game(dbCur, gameId)

    print(gameMoves)
    return render_template('moves.html', gameMoves=gameMoves)



if __name__ == "__main__":
    app.run()
