from flask import Flask,render_template,url_for,request,redirect,session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re




app = Flask(__name__)
app.secret_key ="secret key"

#database connection 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'S549862a'
app.config['MYSQL_DB'] = 'pythonlogin'

#MySql init
mysql = MySQL(app)

@app.route('/pythonlogin',methods=['GET','POST'])
def login():
    msg = ""
    
    
    # checking if username and password is entered via POST
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
            
        #checking if account is in database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s',(username,password,))
        account = cursor.fetchone()
        
        if account:
            
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        
        else:
            msg = 'Incorrect username or password'
    
    return render_template('index.html',msg=msg)

@app.route('/logout')
def logout():
    
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('username',None)
    
    return redirect(url_for('login'))


@app.route('/register',methods= ['GET','POST'])
def register():
    
    msg = ''
    # checking if username, password and email POST requests exist in form
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        #checking if account exists in database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
        
    elif request.method == 'POST':
        msg = "fill up form please"
        
    return render_template('register.html',msg=msg)
        
@app.route('/home')
def home():
    
    #checking if user is logged in
    if 'loggedin' in session:
        
        return render_template('home.html', username=session['username'])
    
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    
    if 'loggedin' in session:
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s',(session['id'],))
        account = cursor.fetchone()
        
        return render_template('profile.html',account=account)

    return redirect(url_for('login'))                     



if __name__ == '__main__':
    app.run(debug=True)