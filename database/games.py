import random
import logging
from mysql.connector import Error
from database.users import *
import MySQLdb.cursors

get_all_active_games_by_both_user_id = None

class Games:
    def add_game(dbCur, userOne, userTwo, bag, rackOne, rackTwo):
        try:
            logging.debug("Adding game into db")
            dbCur.execute("INSERT into games(user_id_one, user_id_two, user_id_one_score, user_id_two_score, winner_user_id, \
            active_game, current_users_turn, bag, user_one_rack, user_two_rack) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
            (userOne, userTwo, 0, 0, None, True, userOne, bag, rackOne, rackTwo))
            return dbCur.lastrowid
        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()

    def get_game_by_id(dbCur, gameId):
        try:
            logging.debug("Getting game by id: %s", gameId)
            dbCur.execute("SELECT * FROM games where game_id = %s", (gameId,))
            game = dbCur.fetchone()
            return game
        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()

    def get_active_game_by_id(dbCur, gameId):
        try:
            logging.debug("Getting game by id: %s", gameId)
            dbCur.execute("SELECT * FROM games where game_id = %s and active_game = True", (gameId,))
            game = dbCur.fetchone()
            return game
        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()
    
    def update_game_score(self, dbCur, gameId, userId, userScore):
        try:
            logging.debug("Updating user's: %s score for game: %s", userId, gameId)
            game = self.get_game_by_id(dbCur, gameId)
            userOne = game['user_id_one']
            userTwo = game['user_id_two']
            userOneScore = game['user_id_one_score']
            userTwoScore = game['user_id_two_score']
            currentPlayer = game['current_users_turn']
            # TO-DO: send usernames in via param?
            playerOne = Users.get_user_by_user_id(Users, dbCur, userOne)
            playerOneUserName = playerOne['username']

            playerTwo = Users.get_user_by_user_id(Users, dbCur, userTwo)
            playerTwoUsername = playerTwo['username']

            # current user is user_id_one
            if str(userId) == str(userOne):
                userOneScore = userOneScore + userScore
                rack = game['user_two_rack']
                logging.debug("setting user's: %s score to: %s", userOne, userOneScore)
                dbCur.execute("UPDATE games SET user_id_one_score = %s, current_users_turn = %s WHERE game_id = %s and active_game = True", (userOneScore, userTwo, gameId))
                return({'currentUserNameTurn':playerTwoUsername, 'currentUserIdTurn':playerTwo['login_id'], 'playerOne':playerOneUserName, 'playerTwo':playerTwoUsername,'playerOneScore':userOneScore, 'playerTwoScore':userTwoScore, 'rack':rack})
            # current user is user_id_two
            else:
                userTwoScore = userTwoScore + userScore
                rack = game['user_one_rack']
                logging.debug("setting user's: %s score to: %s", userTwo, userTwoScore)
                dbCur.execute("UPDATE games SET user_id_two_score = %s, current_users_turn = %s WHERE game_id = %s and active_game = True", (userTwoScore, userOne, gameId))
                return({'currentUserNameTurn':playerOneUserName, 'currentUserIdTurn':playerOne['login_id'], 'playerOne':playerOneUserName, 'playerTwo':playerTwoUsername, 'playerOneScore':userOneScore, 'playerTwoScore':userTwoScore, 'rack':rack})

        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()



    # gets all ACTIVE games played by two specific players
    def get_all_active_games_by_both_user_id(dbCur, user_one, user_two):
        try:
            logging.debug("Getting all ACTIVE games played by users: %s and %s", user_one, user_two)
            dbCur.execute('SELECT game_id FROM games where ((user_id_one = %s AND user_id_two = %s) OR (user_id_one = %s AND user_id_two = %s)) AND active_game = True', 
                (user_one, user_two, user_two, user_one))
            returnedValue = dbCur.fetchone()
            if returnedValue != None:
                gameId = (returnedValue['game_id'])
                logging.info("Returning game_id: %s", gameId)
                return gameId
            return None
        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()
            
    def game_finished(self, dbCur, user_one, user_two, winner):
        try:
            gameId = self.get_all_active_games_by_both_user_id(dbCur, user_one, user_two)
            logging.debug("Updating finished game for game_id: %s", gameId)
            dbCur.execute("UPDATE games SET winner_user_id = %s, active_game = False WHERE game_id = %s", (winner, gameId))
            # dbCur.commit()
            logging.info("Updated finished game")
            return

        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()

    # gets all active games for one specific user
    def get_all_active_games_for_single_user_id(dbCur, username):
        try:
            # dbCur = db.connection.cursor(MySQLdb.cursors.DictCursor)
            logging.debug("Getting active game played by user: %s", username)
            # dbCur = db.cursor()
            dbCur.execute('SELECT * FROM games where (user_id_one = %s OR user_id_two = %s) AND active_game = True', (username, username))
            game = dbCur.fetchone()
            return game
        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()


    # gets all games played by one specific user
    def get_all_games_by_single_user_id(dbCur, username):
        try:
            logging.debug("Getting all games played by user: %s", username)
            # dbCur = db.cursor()
            dbCur.execute('SELECT * FROM games where (user_id_one = %s OR user_id_two = %s) AND active_game = False', (username,username))
            return dbCur.fetchall()
            # for row in dbCur.fetchall():
            #     return row
            # TO-DO add return statement if needed
        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()

    # gets all the games played by two specific players
    def get_all_games_by_both_user_id(db, user_one, user_two):
        try:
            logging.debug("Getting all games played by users: %s and %s", user_one, user_two)
            dbCur = db.cursor()
            dbCur.execute('SELECT * FROM games where (user_id_one = %(user_one)s AND user_id_two = %(user_two)s) OR (user_id_one = %(user_two)s AND user_id_two = %(user_one)s)', 
                {'user_one': user_one}, {'user_two': user_two})
            for row in dbCur.fetchall():
                logging.debug(row)
            # TO-DO add return statement if needed
        except Error as err:
            logging.error("Error: %s", err)
            db.close()

    def get_all_games(db):
        try:
            logging.debug("Getting all games")
            dbCur = db.cursor()
            dbCur.execute('SELECT * FROM games')
            for row in dbCur.fetchall():
                logging.debug(row)
            # TO-DO add return statement if needed
        except Error as err:
            logging.error("Error: %s", err)
            db.close()
