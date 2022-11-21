import pymysql
from flask import Flask, render_template, request, redirect, url_for, session
import re
from board.bag import *
from database.users import *
from game_play import *

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

bag = Bag()



if __name__=='__main__':
    app.run()
