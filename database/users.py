import random
import logging
from mysql.connector import Error

class Users:

    def add_user(db, username):
        try:
            id = random.getrandbits(32)
            # TO-DO: do we want to pass in the db? or the cursor? or initialize it every time?
            dbCur = db.cursor()
            logging.debug("Adding user into db")
            dbCur.execute("INSERT into users(user_id, username, win, loss) values(%s, %s, %s, %s)", (id, username, 0, 0))
            # TO-DO: are we ok with how I create the user_id?
            db.commit()
            logging.info("Inserted user into table with id: %s", str(id))
            return id
        except Error as err:
            logging.error("Error: %s", err)
            db.close()

    def get_users_win_rate(db, username):
        try:
            dbCur = db.cursor()
            logging.debug("Getting user: %s's win rate", username)
            dbCur.execute("SELECT win FROM users WHERE username = %s", (username,))
            # TO-DO add log to catch an error if fetchone is empty
            winResults = (dbCur.fetchone()[0])
            logging.info("User: %s's current wins: %s", username, winResults)
            return winResults
        except Error as err:
            logging.error("Error: %s", err)
            db.close()

    def set_user_won(db, username):
        try:
            winResults = getUsersWinRate(db, username) + 1
            dbCur = db.cursor()
            logging.debug("Changing user: %s's win rate to: %s", username, winResults)
            dbCur.execute("UPDATE users SET win = %s WHERE username = %s", (winResults, username))
            db.commit()
            logging.info("Updated user: %s's win rate to: %s", username, winResults)

        except Error as err:
            logging.error("Error: %s", err)
            db.close()

    def get_users_loss_rate(db, username):
        try:
            dbCur = db.cursor()
            logging.debug("Getting user: %s's loss rate", username)
            dbCur.execute("SELECT loss FROM users WHERE username = %s", (username,))
            # TO-DO add log to catch an error if fetchone is empty
            lossResults = (dbCur.fetchone()[0])
            logging.info("User: %s's current losses: %s", username, lossResults)
            return lossResults
        except Error as err:
            logging.error("Error: %s", err)
            db.close()


    def set_user_lost(db, username):
        try:
            lossResults = getUsersLossRate(db, username) + 1
            dbCur = db.cursor()
            logging.debug("Changing user: %s's loss rate to: %s", username, lossResults)
            dbCur.execute("UPDATE users SET loss = %s WHERE username = %s", (lossResults, username))
            db.commit()
            logging.info("Updated user: %s's loss rate to: %s", username, lossResults)

        except Error as err:
            logging.error("Error: %s", err)
            db.close()


    def get_user(db, username):
        try:
            logging.debug("Getting user: %s", username)
            dbCur = db.cursor()
            dbCur.execute('SELECT * FROM users where username = %s', (username,))
            user = (dbCur.fetchone())
            logging.info("Returning user: %s", str(user))
            return user
        except Error as err:
            logging.error("Error: %s", err)
            db.close()


    # def get_all_users(db):
    #     try:
    #         dbCur = db.cursor()
    #         dbCur.execute('SELECT * FROM users')
    #         for row in dbCur.fetchall():
    #             print(row)
    #         # TO-DO add return statement if needed
    #     except Error as err:
    #         print(f"Error: '{err}'")
    #         db.close()