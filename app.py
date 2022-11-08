#Python login tutorial - #https://webdamn.com/login-and-registration-with-python-flask-mysql/
from Flask import flask, render_template, request, redirect, url_for, session
from flask_mysqldb import mysql
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'test'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] ='user-system'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])

def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = reqest.form['password']
        cursor = mysql.connection.curson(MySQLdb.cursors.DictCursor)
        cursors.execute('SELECT * FROM user WHERE email = %s AND password = %s',(email,password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return render_template('user.html', message = message)
        else:
            message = "Please enter correct email/password."
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/register', methods = ['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user WHERE email =%s", (email, ))
        account = cursor.fetchone()
        if account:
            message = "Account already exist!"
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = "Invalid email address!"
        elif not userName or not password or not email:
            message = "Please fill out the form!"
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s)', (userName, email, password))
            mysql.connection.commit()
            message = "You have successfully registered!"
        elif request.method =="POST":
            message = "Please fill out the form."
        return render_template("register.html", message = message)

if __name__ == "__main__":
    app.run()
