import random
from mysql.connector import Error

# TO-DO: change print statements to log statements


def addUser(db, username):
    try:
        # TO-DO: do we want to pass in the db? or the cursor? or initialize it every time?
        dbCur = db.cursor()
        print('adding user into db')
        dbCur.execute("INSERT into users(user_id, username, win, loss) values(%s, %s, %s, %s)", (random.getrandbits(32), username, 0, 0))
        # TO-DO: are we ok with how I create the user_id?
        db.commit()
        print('inserted user')

    except Error as err:
        print(f"Error: '{err}'")
        db.close()

def getUsersWinRate(db, username):
    try:
        dbCur = db.cursor()
        print("getting user's win rate")
        dbCur.execute("SELECT win FROM users WHERE username = %s", (username,))
        # TO-DO add log to catch an error if fetchone is empty
        winResults = (dbCur.fetchone()[0])
        print("user's current wins: " + winResults)
        return winResults
    except Error as err:
        print(f"Error: '{err}'")
        db.close()

def setUserWon(db, username):
    try:
        winResults = getUsersWinRate(db, username) + 1
        dbCur = db.cursor()
        print("changing user's win rate to: " + winResults)
        dbCur.execute("UPDATE users SET win = %s WHERE username = %s", (winResults, username))
        db.commit()
        print("updated user's win rate")

    except Error as err:
        print(f"Error: '{err}'")
        db.close()

def getUsersLossRate(db, username):
    try:
        dbCur = db.cursor()
        print("getting user's loss rate")
        dbCur.execute("SELECT loss FROM users WHERE username = %s", (username,))
        # TO-DO add log to catch an error if fetchone is empty
        lossResults = (dbCur.fetchone()[0])
        print("user's current losses: " + lossResults)
        return lossResults
    except Error as err:
        print(f"Error: '{err}'")
        db.close()


def setUserLost(db, username):
    try:
        lossResults = getUsersLossRate(db, username) + 1
        dbCur = db.cursor()
        print("changing user's loss rate to: " + lossResults)
        dbCur.execute("UPDATE users SET loss = %s WHERE username = %s", (lossResults, username))
        db.commit()
        print("updated user's loss rate")

    except Error as err:
        print(f"Error: '{err}'")
        db.close()


def getUser(db, username):
    try:
        dbCur = db.cursor()
        dbCur.execute('SELECT * FROM users where username = %s', (username,))
        user = (dbCur.fetchone()[0])
        print("returning user: " + user)
        return user
    except Error as err:
        print(f"Error: '{err}'")
        db.close()


def getAllUsers(db):
    try:
        dbCur = db.cursor()
        dbCur.execute('SELECT * FROM users')
        for row in dbCur.fetchall():
            print(row)
        # TO-DO add return statement if needed
    except Error as err:
        print(f"Error: '{err}'")
        db.close()