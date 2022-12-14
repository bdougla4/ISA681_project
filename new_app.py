import pymysql
from flask import Flask, render_template, request, redirect, url_for, session
import re
import logging
from board.bag import *
from board.rack import *
from database.users import *
from database.games import *
from database.moves import *
from game_play import *

# TO-DO: do we want to log things to a file? 
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = 'isa681Scrabble'

#connecting to MySQL database
db = pymysql.connect(host="localhost", user="root", password="", database="scrabble")

dbCur = db.cursor()

#remove the following try/except. only used for debbuging purposes
# try:
#     dbCur.execute('SELECT * FROM users')
#     for row in dbCur.fetchall():
#         print(row)
# except:
#     print("Error: Unable to fetch data. Does Databse exist?")
#     db.close()

# @app.route('/')
# @app.route('/login', methods = ['GET','POST'])
# def log():
#     ''' Login function for Scrabble game. '''
#     msg = ''
#     if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
#         email = request.form['email']
#         passwd = request.form['password']
#         dbCur.execute('SELECT * FROM user WHERE email = %s AND password= %s', (email, passwd))
#         user = cursor.fetchone()
#         if user:
#             session['loggedin'] = True
#             session['userid'] = user['userid']
#             session['name'] = user['name']
#             session['email'] = user['email']
#             msg = 'Logged in successfully!'
#             return render_template('user.html',msg = msg)
#         else:
#             msg = 'Incorrect username/password!'
#     return render_template('login.html', msg = msg)

# @app.route('/logout')
# def logout():
#     session.pop('loggedin', None)
#     session.pop('userid', None)
#     session.pop('email', None)
#     return redirect(url_for('login'))

# @app.route('/register', methods=['GET','POST'])
# def register():
#     '''Scrabble Registration routine for accounts not found in the MySQL database.'''
#     msg =''
#     if request.method =='POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
#         userName = request.form['name']
#         password = request.form['password']
#         email = request.form['email']
#         dbCur.execute('SELECT * FROM user WHERE email = % s', (email, ))
#         account = dbCur.fetchone()
#         if account:
#             msg ="You are now registered. Enjoy playing"
#         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
#             msg = "Invalid email address!"
#         elif not userName or not password or not email:
#             msg = "Please complete required fields."
#         else:
#             dbCur.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
#             db.commit()
#             msg = 'You are now registered!'
#     elif request.method == 'POST':
#         msg = "Please complete the required fields."
#     return render_template('register.html', msg = msg)




# print(bag)
# print(rack.get_rack_str())
# print("A" in rack.get_rack_arr())
# for tile in rack.get_rack_arr():
#     print(tile.get_letter())
# print(rack.get_rack_arr())

# order:
# - determine if row / col is in bounds
# - determine if user's word is using the correct available letters

print('creating bag and rack')
bag = Bag()
rack = Rack(bag)

# create users
print('creating new users')
userId1 = Users.add_user(db, "user1")
userId2 = Users.add_user(db, "user2")
print('\n')
# create game
print('creating new game \n')
gameId = Games.add_game(db, userId1, userId2)
userId = userId1


def get_user_position():
    continueBlock = False
    while(continueBlock == False):
        print('\n')
        # get user's position
        # TO-DO: get row and col and do checks on it 
        positionInput = input("get position ")
        positionAllowed = GamePlay.is_position_allowed(positionInput)
        if positionAllowed == True:
            continueBlock = True
            return positionInput

def get_user_word(positionInput):
    print('\n')
    # get user's word
    wordInput = input("Create a word longer than 2 letters using the letters in your rack, or enter ### to skip a turn \n")
    if len(wordInput) < 2:
        print("word must be longer than 2 letters. Try again \n")
        get_user_word(positionInput)
    # TO-DO: using regex might be difficult here since our racks are dynamic
    for letter in wordInput:
        if letter.upper() not in rack.get_rack_str():
            print("'" + letter + "'" + ' not in rack. Try again')
            get_user_word(positionInput)
    # skip functionality
    if(wordInput == "###"):
        print('User skipped turn')
        Moves.add_move(db, gameId, userId, None, 0, True, 0, 0, positionInput)
    else: 
        isWord = GamePlay.is_word_in_dictionary(wordInput)
        # TO-DO: do we want a loop if word is not in dictionary?
        if(isWord):
            points = GamePlay.calculate_word_score(wordInput)
            Moves.add_move(db, gameId, userId, wordInput, points, False, 0, 0, positionInput)
        else:
            print('word is not in dictionary. No points calculated')
            Moves.add_move(db, gameId, userId, wordInput, 0, False, 0, 0, positionInput)

def turn(userId):
    print("\nuserId's turn: " + str(userId) + "\n")
    print("\nThese are the letters in your rack: " + rack.get_rack_str())

    positionInput = get_user_position()
    get_user_word(positionInput)


while True:
    if(userId == userId2):
        userId = userId1
    else: 
        userId = userId2
    # user's turn
    turn(userId)




    







if __name__=='__main__':
    app.run()
