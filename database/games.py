import random
from mysql.connector import Error
from datetime import date

# TO-DO: change print statements to log statements
class Games:

    def add_game(db, user_one, user_two):
        try:
            id = random.getrandbits(32)
            # TO-DO: do we want to pass in the db? or the cursor? or initialize it every time?
            dbCur = db.cursor()
            print('adding game into db')
            dbCur.execute("INSERT into games(game_id, username_id_one, username_id_two, winner_user_id, date_played, active_game) values(%s, %s, %s, %s, %s, %s)", 
            (id, user_one, user_two, None, date.today(), True))
            # TO-DO: are we ok with how I create the game_id?
            db.commit()
            print('inserted game with id: ' + str(id))
            return id
        except Error as err:
            print(f"Error: '{err}'")
            db.close()

    # TO-DO: if the game was forfeited or closed, who wins?
    def game_finished(db, user_one, user_two, winner):
        try:
            gameId = get_all_active_games_by_both_user_id(db, user_one, user_two)
            dbCur = db.cursor()
            print("updating finished game for game_id " + gameId)
            dbCur.execute("UPDATE games SET winner_user_id = %s active_game = False WHERE game_id = %s", (winner, gameId))
            db.commit()
            print("updated finished game")

        except Error as err:
            print(f"Error: '{err}'")
            db.close()

    # gets all games played by one specific user
    def get_all_games_by_single_user_id(db, username):
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
    def get_all_games_by_both_user_id(db, user_one, user_two):
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
    def get_all_active_games_by_both_user_id(db, user_one, user_two):
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

    def get_all_games(db):
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
