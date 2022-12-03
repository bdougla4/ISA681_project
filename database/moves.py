import random
import logging
from mysql.connector import Error

class Moves:

    def add_move(db, gameId, userId, wordCreated, points, turnSkipped, columnNum, rowNum, positionPlayed):
        try:
            dbCur = db.cursor()
            logging.debug("Adding moves for game: %s and user_id: %s into database", str(gameId), str(userId))
            dbCur.execute("INSERT into moves(move_id, game_id, user_id, word_created, points, turn_skipped, column_num, row_num, position_played) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
            (random.getrandbits(32), gameId, userId, wordCreated, points, turnSkipped, columnNum, rowNum, positionPlayed))
            db.commit()
            logging.info("Inserted move")

        except Error as err:
            logging.error("Error: %s", err)
            db.close()


    def get_all_moves_for_game(db, gameId):
        logging.debug("Getting all moves for game_id: %s", str(gameId))
        try:
            dbCur = db.cursor()
            dbCur.execute("SELECT * FROM moves where game_id = %s", (gameId,))
            moves = dbCur.fetchall()
            for row in moves:
                logging.debug(row)
            return moves
        except Error as err:
            logging.error("Error: %s", err)
            db.close()