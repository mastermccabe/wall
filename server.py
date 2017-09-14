from flask import Flask, request, redirect, render_template, session, flash
import re
import md5
# import the Connector function
from mysqlconnection import MySQLConnector
app = Flask(__name__)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# connect and store the connection in "mysql" note that you pass the database name to the function
mysql = MySQLConnector(app, 'thewall')
app.secret_key = "ThisIsSecret!"


# PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$')
# hashed_password = md5.new(password).hexdigest()
# an example of running a query

# print("***************** Users *******************")
# print mysql.query_db("SELECT * FROM users")
# print("****************** USERS ******************")

# print mysql.query_db("SELECT * FROM users")

@app.route('/')
def index():
    # if not 'loggedin' in session:
    #     session['loggedin'] = False
    # else:
    #     session['loggedin'] = True
    #     return redirect('/')
    session['loggedin'] = False

    return render_template('index.html', loggedin=session['loggedin'])


#
@app.route('/signin', methods=['POST'])
def signin():

    # query = "SELECT * from users where email = :email"


    query = "SELECT * FROM users WHERE users.email = :email and users.password = :password"
    data = {
            'email': request.form['email'],
            'password': md5.new(request.form['password']).hexdigest()
    }
    value = mysql.query_db(query, data)
    if len(value)==0:
        flash("Invalid email or password")
        loggedin = False
        return redirect('/')
    else:
        session['user_info'] = value
        session['loggedin'] = True

        return redirect('/wall')
  #   user = mysql.query_db(user_query, query_data)
  #   if len(user) != 0:
  #       encrypted_password = password
  #       # encrypted_password = md5.new(password + user[0]['salt']).hexdigest()
  #       if user[0]['password'] == encrypted_password:
  #       # this means we have a successful login!
  #       else:
  #       # invalid password!
  #   else:
  # # invalid email!

@app.route('/wall')
def wall():
    if session['loggedin'] == True:

        info = session['user_info']
    # first_name = session['first_name']
    print info
    # info = "SELECT * FROM users where"
    # if not 'loggedin' in session:
    #     session['loggedin'] = False
    # else:
    #     session['loggedin'] = False
    #     return redirect('/')

    # if loggedin == False:
    #     return render_template('index.html', loggedin = loggedin)
    # else:

    return render_template('wall.html')


@app.route('/signout',methods= ['POST'])
def sign_out():
    # button = request.form['button']
    # session['counter']=0
    session.pop('loggedin')
    return redirect('/')

@app.route('/signup', methods=['POST'])
def create_user():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password2 = request.form['password']
    conf_password2 = request.form['conf_password']
    password = md5.new(request.form['password']).hexdigest()
    # conf_password = request.form['conf_password'].hexidigest()
    query = "SELECT * from users where email = :email"

    if len(request.form['email']) <1:
        flash("email cannot be blank")
        return redirect('/')

    elif not EMAIL_REGEX.match(request.form['email']):
        flash("invalid email address")
    elif len(request.form['first_name']) < 1:
        flash("first name cannot be blank!")
        return redirect('/')
    elif len(request.form['last_name']) <1:
        flash("lastname cannot be blank")
        return redirect('/')
    elif len(request.form['email']) < 1:
       flash("password cannot be blank")
       return redirect('/')
    elif len(request.form['password']) <4:
       flash("password must be greater than 4 characters")
       return redirect('/')
    # elif not PASSWORD_REGEX.match(request.form['password']):
    #     flash('Password must contain at least one lowercase letter, one uppercase letter, and one digit', 'passwordError')
    #     return redirect('/')
    elif not password2 == conf_password2:
        flash("Passwords must match")
        return redirect('/')

    else:
        data = {
             'email': request.form['email']
           }
        value = mysql.query_db(query, data)
        if not len(value)==0:
            flash('You already have an acount, please try logging in')
            return redirect('/')
        else: insert_query = "INSERT INTO users (last_name, first_name, email, password, created_at, updated_at) VALUES (:last_name, :first_name ,:email, :password, NOW(), NOW())"
        query_data = { 'last_name': last_name,'first_name': first_name,  'email': email, 'password': password }
        mysql.query_db(insert_query, query_data)
        flash("success!!")
        session['loggedin'] = True
        session['user_info'] = query_data
        session['first_name'] = first_name
        return redirect('/')

    return render_template('index.html', first_name = session['first_name'], user_info=session['user_info'])


# Say we wanted to update a specific record, we could create another page and add a form that would submit to the following route:
# @app.route('/update_age', methods=['POST'])
# def update():
#     query = "UPDATE emails SET age = :age WHERE id = :id"
#     data = {
#              'age': request.form['age2'],
#              'id': request.form['user_id2']
#            }
#     mysql.query_db(query, data)
#     return redirect('/')
#
# @app.route('/delete_users', methods=['POST'])
# def delete():
#     query = "DELETE FROM email WHERE id = :id"
#     data = {'id': request.form['user_id']}
#     mysql.query_db(query, data)
#     return redirect('/')
#



app.run(debug=True)
