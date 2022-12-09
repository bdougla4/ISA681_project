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
                return render_template("menu.html", msg=msg)
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
            elif len(request.form['password']) < 8 or\
                re.search((r"(\#)+|(\*)+|\!+|\&+\@+\$+"), escape(request.form['password'])) == None:
                msg = 'Passwords must be a minimum of 8 characters, contain lower and upper case letters, numbers ' \
                      'and at least one special character (acceptable characters: #, *, ! &, @, $).'
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
    # This will force all communications to be exchanged via HTTPS rather than HTTP. 
    app.run(ssl_context="adhoc")
    
    # Upon generation of ssl certs, we will comment out the app.run(ssl_context="adhoc") above and use this line to use our self-signed certificates.
    # app.run(ssl_context='isa681Cert.pem', 'isa681Key.pem')
