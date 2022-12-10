import random
import logging
from mysql.connector import Error

class Moves:

    def add_move(dbCur, gameId, userId, wordCreated, points, turnSkipped, columnNum, rowNum, positionPlayed):
        try:
            # dbCur = db.cursor()
            logging.debug("Adding moves for game: %s and user_id: %s into database", str(gameId), str(userId))
            dbCur.execute("INSERT into moves(game_id, user_id, word_created, points, turn_skipped, column_num, row_num, position_played) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
            (gameId, userId, wordCreated, points, turnSkipped, columnNum, rowNum, positionPlayed))
            # db.commit()
            logging.info("Inserted move")

        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()


    def get_all_moves_for_game(dbCur, gameId):
        logging.debug("Getting all moves for game_id: %s", str(gameId))
        try:
            movesList = []
            # dbCur = db.cursor()
            dbCur.execute("SELECT username, word_created, points, turn_skipped, column_num, row_num, position_played, moves.date_played FROM moves JOIN games ON games.game_id = moves.game_id JOIN users ON moves.user_id = users.user_id WHERE (moves.game_id = %s AND games.active_game = False) ORDER BY moves.date_played ASC", (gameId,))
            moves = dbCur.fetchall()

            for move in moves:
                if move['turn_skipped'] == 0:
                    move['turn_skipped'] = False
                else:
                    move['turn_skipped'] = True
                movesList.append(move)
            return movesList
        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()