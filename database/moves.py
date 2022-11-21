import random
from mysql.connector import Error

# TO-DO: change print statements to log statements
class Moves:

    def add_move(db, gameId, userId, wordCreated, points, turnSkipped, columnNum, rowNum, positionPlayed):
        try:
            dbCur = db.cursor()
            print('adding move for game ' + str(gameId) + ' and userId: ' + str(userId) + ' into db')
            dbCur.execute("INSERT into moves(move_id, game_id, user_id, word_created, points, turn_skipped, column_num, row_num, position_played) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
            (random.getrandbits(32), gameId, userId, wordCreated, points, turnSkipped, columnNum, rowNum, positionPlayed))
            db.commit()
            print('inserted move')

        except Error as err:
            print(f"Error: '{err}'")
            db.close()


    def get_all_moves_for_game(db, gameId):
        print('getting all moves for gameId: ' + gameId)
        try:
            dbCur = db.cursor()
            dbCur.execute("SELECT * FROM moves where game_id = %s", (gameId,))
            moves = dbCur.fetchall()
            for row in moves:
                print(row)
            return moves
        except Error as err:
            print(f"Error: '{err}'")
            db.close()