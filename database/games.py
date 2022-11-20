import random
from mysql.connector import Error
from datetime import date

# TO-DO: change print statements to log statements


def addGame(db, user_one, user_two):
    try:
        # TO-DO: do we want to pass in the db? or the cursor? or initialize it every time?
        dbCur = db.cursor()
        print('adding game into db')
        dbCur.execute("INSERT into games(game_id, username_id_one, username_id_two, winner_user_id, date_played, active_game) values(%s, %s, %s, %s, %s, %s)", 
        (random.getrandbits(32), user_one, user_two, None, date.today(), True))
        # TO-DO: are we ok with how I create the game_id?
        db.commit()
        print('inserted game')

    except Error as err:
        print(f"Error: '{err}'")
        db.close()

# TO-DO: if the game was forfeited or closed, who wins?
def gameFinished(db, user_one, user_two, winner):
    try:
        gameId = getAllActiveGamesByBothUserId(db, user_one, user_two)
        dbCur = db.cursor()
        print("updating finished game for game_id " + gameId)
        dbCur.execute("UPDATE games SET winner_user_id = %s active_game = False WHERE game_id = %s", (winner, gameId))
        db.commit()
        print("updated finished game")

    except Error as err:
        print(f"Error: '{err}'")
        db.close()

# gets all games played by one specific user
def getAllGamesBySingleUserId(db, username):
    try:
        print('getting all games played by user: ' + username)
        dbCur = db.cursor()
        dbCur.execute('SELECT * FROM games where username_id_one = %s OR username_id_two = %s', (username,))
        for row in dbCur.fetchall():
            print(row)
        # TO-DO add return statement if needed
    except Error as err:
        print(f"Error: '{err}'")
        db.close()

# gets all the games played by two specific players
def getAllGamesByBothUserId(db, user_one, user_two):
    try:
        print('getting all games played by users: ' + user_one + ' and ' + user_two)
        dbCur = db.cursor()
        dbCur.execute('SELECT * FROM games where (username_id_one = %(user_one)s AND username_id_two = %(user_two)s) OR (username_id_one = %(user_two)s AND username_id_two = %(user_one)s)', 
            {'user_one': user_one}, {'user_two': user_two})
        for row in dbCur.fetchall():
            print(row)
        # TO-DO add return statement if needed
    except Error as err:
        print(f"Error: '{err}'")
        db.close()

# gets all ACTIVE games played by two specific players
def getAllActiveGamesByBothUserId(db, user_one, user_two):
    try:
        print('getting all ACTIVE games played by users: ' + user_one + ' and ' + user_two)
        dbCur = db.cursor()
        dbCur.execute('SELECT game_id FROM games where ((username_id_one = %(user_one)s AND username_id_two = %(user_two)s) OR (username_id_one = %(user_two)s AND username_id_two = %(user_one)s)) AND active_game = True', 
            {'user_one': user_one}, {'user_two': user_two})
        gameId = (dbCur.fetchone()[0])
        print("game_id returned: " + gameId)
        return gameId
    except Error as err:
        print(f"Error: '{err}'")
        db.close()

def getAllGames(db):
    try:
        print('getting all games')
        dbCur = db.cursor()
        dbCur.execute('SELECT * FROM games')
        for row in dbCur.fetchall():
            print(row)
        # TO-DO add return statement if needed
    except Error as err:
        print(f"Error: '{err}'")
        db.close()
