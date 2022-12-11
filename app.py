""" ISA681 Scrabble python main file.
    python app.py will get the Scrabble game going.
    Authors: Veeda Sherzadah <vsherzad@gmu.edu> & Brienne Douglas (bdougla4@gmu.edu)
    Fall 2022
    December 10, 2022
"""
from flask import escape, Flask, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin
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
from board.rack import *
from board.bag import *

# Loading .env file to keep database username/passwords from being hardcoded into source code.
from dotenv import load_dotenv
load_dotenv()

# Logging functionalilty for informational (and debugging) purposes.
# logging.basicConfig(filename='app.log', filemode='a', encoding='utf-8', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

userid2 = 2
user2name = "user2"

app = Flask(__name__)

# Random 24 bit string for session key.
app.secret_key = os.urandom(24)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'scrabble'

# Loading flask-login Login Manager to assist with joining multiple login sessions for game play.
# loginManger = LoginManger()
# loginManger.init_app(app)


# Connecting to MySQL database (MYSQL_DB)
db = MySQL(app)

# GLOBAL VARIABLES
attempts = 0  # logging number of password entry attempts for a user.
# class User(UserMixin, db):
#     cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
#     user = cursor.execute()


@app.route("/")
def homepage():
    """ISA Scrabble general homepage for users to Login, Register View Stats, and Play. """
    return render_template('index.html')

# @app.loginManager.user_loader
# def load_user(username):
#     """ Using flask's login manager feature to assist with maintaining the various logged in users.
#     This will be essential for connecting players to one another for game play.
#     Input variable: username must be of type string for correct use. We will use the session['username'] key as the
#     username for this function. """
#     return User.get(username)


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
                #setting user overall session cookie
                session['loggedin'] = True
                session['id'] = account['login_id']
                session['name'] = account['username']
                session['email'] = account['email']
                msg = "Welcome " + username + "!"
                logging.info("Logging sessionID: %s, user: %s, email: %s." % (session['id'], session['name'],
                                                                              session['email']))
                # if Games.get_all_active_games_for_single_user_id(cursor, session['id']) != None:
                #     activeGame = True
                #     logging.info("User has active game")
                # return render_template("menu.html", activeGame=activeGame, msg=msg)
                return redirect(url_for('menu'))
            else:
                msg = "Incorrect Username/Password!"
                logging.info("Invalid login attempt user: %s, email: %s." % (account['username'], account['email']))
                return render_template('login.html', msg=msg)
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out.
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
            elif len(request.form['password']) < 8 or len(request.form['password']) > 20 or\
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
                loginId = cursor.lastrowid
                logging.debug("Created Login. Now creating user for login")
                # cursor.execute('SELECT login_id FROM login WHERE username = %s', (username,))
                # loginId = (cursor.fetchone())['login_id']
                Users.add_user(cursor, loginId, username)
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
    """ Function route for the Scrabble main menu. Page will render options for user to join a game, see current games,
    and check their win/loss stats."""
    activeGame = False
    logging.info("Checking for active games for user.")
    dbCur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    if Games.get_all_active_games_for_single_user_id(dbCur, session['id']) != None:
        activeGame = True
        logging.info("User has active game")

    logging.info("Active game = %s", activeGame)
    return render_template('menu.html', activeGame=activeGame, gameForfeited=False)


@app.route('/game/', methods=['GET', 'POST'])
def game():
    displayUndefinedError = None
    displayForfeitError = None
    displayNotInRackError = None
    playerStats = None
    # rack = None
    print('')
    print('')
    print('')
    print('in game')
    print('')
    print('')
    print('')
    print('')
    print('')
    print('')
    print('')
    print(session)
    # currentGame = Games.get_all_active_games_for_single_user_id(dbCur, session['id'])
    # print(session['rackOne'])
    # print(session['rackTwo'])
    # print(session['userOneId'])
    # print(session['userTwoId'])
    # print(session['userOneName'])
    # print(session['userTwoName'])
    # print(session['userIdTurn'])
    # print(session['userNameTurn'])
    print('')
    print('')
    print('')
    print('')
    # print(currentGame)
    print('')
    print('')
    print('')
    print('')
    print('')

    try:
        dbCur = db.connection.cursor(MySQLdb.cursors.DictCursor)
        logging.debug("user wants to continue previous game. checking if user has active game")
        currentGame = Games.get_all_active_games_for_single_user_id(dbCur, session['id'])
        if currentGame != None:
            logging.info("user has active game")
            playerStats = GamePlay.generate_continue_game_stats(dbCur, currentGame)
        else:
            raise UserForfeitedException("Other user forfeited during game play")
        # if ('gameStatus' in request.args):
        #     gameStatus = request.args.get('gameStatus')
        #     if gameStatus == 'continue':
        #         logging.debug("user wants to continue previous game. checking if user has active game")
        #         # TO-DO: get user id
        #         currentGame = Games.get_all_active_games_for_single_user_id(dbCur, session['id'])
        #         if currentGame != None:
        #             logging.info("user has active game")
        #             playerStats = GamePlay.generate_continue_game_stats(dbCur, currentGame)
        #         else:
        #             raise UserForfeitedException("Other user forfeited during game play")

        if (session.get('rackOne') == None):
            logging.debug("Can not find rack in session. Need to generate old session keys")
            generate_old_session(dbCur, currentGame)
        if (currentGame['current_users_turn'] == session['id']):
            rack = session['rackOne']
        else:
            rack = session['rackTwo']

        if ('submit-user-input' in request.form and ('user-word' in request.form and request.form['user-word'] != '') and 
        ('user-position' in request.form and request.form['user-position'] != '') 
        and ('col' in request.form and request.form['col'] != '') and ('row' in request.form and request.form['row'] != '')):
            logging.debug('user submitted position, word, row, and column')
            position = str(escape(request.form["user-position"]))
            word = str(escape(request.form["user-word"]))
            col = str(escape(request.form["col"]))
            row = str(escape(request.form["row"]))


            # TO-DO: make sure it is user's turn when inserting move
            playerStats = GamePlay.handle_users_input(GamePlay, dbCur, currentGame['game_id'], session['userIdTurn'], 
            word, position, col, row, rack)
            session['userNameTurn'] = playerStats['currentUserNameTurn']
            session['userIdTurn'] = playerStats['currentUserIdTurn']
            rack=playerStats['rack']
            db.connection.commit()
    except UserForfeitedException as err:
        logging.warning("Other user forfeited during game play. Displaying error to UI")
        displayForfeitError = True
    except LettersNotInRackException as err:
        logging.warning("User's input does not use letters in rack. Displaying error to UI")
        displayNotInRackError = True
    except UndefinedWordException as err:
        logging.warning("User's input was invalid. Displaying error to UI")
        displayUndefinedError = True

            
    return render_template('game.html', gameStatus='continue', playerStats=playerStats, 
        displayUndefinedError=displayUndefinedError, displayForfeitError=displayForfeitError, 
        displayNotInRackError=displayNotInRackError, rack=rack)

def generate_old_session(dbCur, currentGame):
    logging.debug("generating old session based on current game stats")

    session['userOneId'] = currentGame['user_id_one']
    session['userTwoId'] = currentGame['user_id_two']

    session['userIdTurn'] = currentGame['current_users_turn']

    if (session['userOneId'] == session['id']):
        user = Users.get_user_by_user_id(Users, dbCur, currentGame['user_id_two'])
        session['userOneName'] = session['name']
        session['userTwoName'] = user['username']
        session['userNameTurn'] = user['username']

    else:
        user = Users.get_user_by_user_id(Users, dbCur, currentGame['user_id_one'])
        session['userOneName'] = user['username']
        session['userTwoName'] = session['name']
        session['userNameTurn'] = user['username']

    session['rackOne'] = currentGame['user_one_rack']
    session['rackTwo'] = currentGame['user_two_rack']

    print('')
    print('')
    print('')
    print('generated old session')
    print('')
    print('')
    print('')
    print('')
    print('')
    print('')
    print('')
    print(session)


@app.route('/new-game/', methods=['GET', 'POST'])
def newGame():
    # TO-DO: get userid from actual user
    dbCur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    logging.debug("user: %s is requesting to join new game", session['name'])

    logging.debug("Making sure user does not have an active game already")
    userid = session['id']
    username = session['name']
    activeGames = Games.get_all_active_games_for_single_user_id(dbCur, userid)

    if activeGames != None:
        logging.warn('User: %s is requesting a new game but already has an active one running', userid)
    else:
        logging.debug('User has no active games currently.')
        logging.debug('Creating new bag.')
        bag = Bag()
        logging.debug('Creating new racks.')
        userOneRack = Rack(bag)
        userTwoRack = Rack(bag)
        session['rackOne'] = userOneRack.get_rack_str()
        session['rackTwo'] = userTwoRack.get_rack_str()

        session['userOneId'] = userid
        session['userTwoId'] = userid2

        session['userOneName'] = username
        session['userTwoName'] = user2name

        session['userIdTurn'] = userid
        session['userNameTurn'] = username

        print('')
        print('')
        print('')
        print('in new game')
        print('')
        print('')
        print('')
        print('')
        print('')
        print('')
        print('')
        print('')
        print(session['rackOne'])
        print(session['rackTwo'])
        print(session['userOneId'])
        print(session['userTwoId'])
        print(session['userOneName'])
        print(session['userTwoName'])
        print(session['userIdTurn'])
        print(session['userNameTurn'])
        print('')
        print('')
        print('')
        print('')
        print('')

        # TO-DO get the correct userids
        gameId = Games.add_game(dbCur, userid, userid2, bag.get_bag_str(), userOneRack.get_rack_str(), userTwoRack.get_rack_str())
        db.connection.commit()
        # session['gameId'] = gameId
        # newGame = Games.get_game_by_id(dbCur, gameId)
        # No longer needed due to session storage
        # playerStats = GamePlay.generate_new_game_stats(dbCur, newGame, session['userOneId'], session['userTwoId'], session['userOneName'], session['userTwoName'])
        playerStats = {'currentUserNameTurn':session['userNameTurn'], 'playerOne':session['userOneName'], 
        'playerTwo':session['userTwoName'], 'playerOneScore':0, 'playerTwoScore':0}
        return redirect(url_for('game', gameStatus='newGame', playerStats=playerStats, rack=session['rackOne']))
        # return render_template('game.html', gameStatus='newGame', playerStats=playerStats, rack=session['rackOne'])
    

@app.route('/end-game/', methods=['GET', 'POST'])
def forfeitGame():
    # TO-DO: get userid from actual user
    dbCur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    logging.info("user: %s forfeited game", session['id'])

    # TO-DO get the correct userid to mark as winner
    Games.game_finished(Games, dbCur, session['id'], userid2, userid2)

    # TO-DO get the correct userid to mark as winner
    Users.set_user_lost(Users, dbCur, session['id'])

    # TO-DO get the correct userid to mark as winner
    Users.set_user_won(Users, dbCur, userid2)

    db.connection.commit()
    return render_template('menu.html', activeGame=False, gameForfeited=True)

@app.route('/scoreboard/', methods=['GET', 'POST'])
def scoreboard():
    userScore = request.args.get('user-score')
    if request.method == 'GET' and (('username' in request.args) or
                                    ('user-score' in request.args) or ('self-score' in request.args)):
        if ((userScore == None) or (userScore == '')):
            username = session['name']
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
    username = session['name']

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
    
    # Use the following with OpenSSL keys generated for on a system. 
    # app.run(host="0.0.0.0", ssl_context=("/etc/apache2/certs/isascrabble.crt", "/etc/apache2/certs/isascrabble.key"))
