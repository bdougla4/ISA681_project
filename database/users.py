import random
import logging
from mysql.connector import Error

get_users_loss_rate = None
get_users_win_rate = None

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

    def get_users_win_rate(self, dbCur, userid):
        try:
            # dbCur = db.cursor()
            logging.debug("Getting user: %s's win rate", userid)
            dbCur.execute("SELECT win FROM users WHERE user_id = %s", (userid,))
            # TO-DO add log to catch an error if fetchone is empty
            returnedValue = (dbCur.fetchone())
            print(returnedValue)
            winResults = (returnedValue['win'])
            logging.info("User: %s's current wins: %s", userid, winResults)
            return winResults
        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()

    def set_user_won(self, dbCur, userid):
        try:
            winResults = self.get_users_win_rate(self, dbCur, userid) + 1
            # dbCur = db.cursor()
            logging.debug("Changing user: %s's win rate to: %s", userid, winResults)
            dbCur.execute("UPDATE users SET win = %s WHERE user_id = %s", (winResults, userid))
            # db.commit()
            logging.info("Updated user: %s's win rate to: %s", userid, winResults)

        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()

    def get_users_loss_rate(self, dbCur, userid):
        try:
            # dbCur = db.cursor()
            logging.debug("Getting user: %s's loss rate", userid)
            dbCur.execute("SELECT loss FROM users WHERE user_id = %s", (userid,))
            # TO-DO add log to catch an error if fetchone is empty
            returnedValue = (dbCur.fetchone())
            lossResults = (returnedValue['loss'])

            logging.info("User: %s's current losses: %s", userid, lossResults)
            return lossResults
        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()


    def set_user_lost(self, dbCur, userid):
        try:
            lossResults = self.get_users_loss_rate(self, dbCur, userid) + 1
            # dbCur = db.cursor()
            logging.debug("Changing user: %s's loss rate to: %s", userid, lossResults)
            dbCur.execute("UPDATE users SET loss = %s WHERE user_id = %s", (lossResults, userid))
            # dbCur.commit()
            logging.info("Updated user: %s's loss rate to: %s", userid, lossResults)

        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()


    def get_user_by_user_id(self, dbCur, userid):
        try:
            logging.debug("Getting user: %s", userid)
            # dbCur = db.cursor()
            dbCur.execute('SELECT * FROM users where user_id = %s', (userid,))
            user = (dbCur.fetchone())
            logging.info("Returning user: %s", str(user))
            return user
        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()



    def get_user_by_user_name(self, dbCur, username):
        try:
            logging.debug("Getting user: %s", username)
            # dbCur = db.cursor()
            dbCur.execute('SELECT * FROM users where username = %s', (username,))
            user = (dbCur.fetchone())
            logging.info("Returning user: %s", str(user))
            return user
        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()


    def get_user_score_board(self, dbCur, username): 
        try:
            usersList = []
            logging.debug("Getting scoreboard for user: %s", username)
            dbCur.execute('SELECT games.game_id, users.username as user1, users.user_id, games.username_id_one, games.username_id_two, games.winner_user_id, games.date_played FROM users JOIN games ON games.username_id_one = users.user_id OR games.username_id_two = users.user_id WHERE (users.username = %s AND games.active_game = False)', (username,))
            users = (dbCur.fetchall())
            for user in users:
                logging.debug("getting all scores for user")
                usersName = user['user1']
                usersId = user['user_id']
                usernameIdOne = user['username_id_one']
                usernameIdTwo = user['username_id_two']
                winnersId = user['winner_user_id']

                returnUserOne = usersName

                if usersId == usernameIdOne:
                    returnUserTwo = (self.get_user_by_user_id(self, dbCur, usernameIdTwo))['username']
                else: 
                    returnUserTwo = (self.get_user_by_user_id(self, dbCur, usernameIdOne))['username']
                if usersId == winnersId:
                    logging.debug("user: %s was the winner for this game", usersName)
                    returnWinner = returnUserOne
                else:
                    logging.debug("user: %s was not the winner for this game", usersName)
                    returnWinner = returnUserTwo
                
                singleUser = {'gameId':user['game_id'], 'user':returnUserOne, 'opponent':returnUserTwo, 'winner':returnWinner, 'datePlayed':user['date_played']}
                usersList.append(singleUser)
            return usersList
        except Error as err:
            logging.error("Error: %s", err)
            dbCur.close()

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