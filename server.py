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
    if 'loggedin' in session:
        return redirect('/wall')
    #     loggedin = session['loggedin']
    else:
    # else:
    #     return redirect('/')
    # if not 'loggedin' in session:
    #     session['loggedin'] = False
    # else:
    #     session['loggedin'] = True
    #     return redirect('/')


        return render_template('index.html')


#
@app.route('/signin', methods=['POST'])
def signin():

    # query = "SELECT * from users where email = :email"


    query = "SELECT * FROM users WHERE users.email = :email and users.password = :password"
    get_id = "SELECT users.user_id FROM users WHERE users.email = :email and users.password = :password"

    data = {
            'email': request.form['email'],
            'password': md5.new(request.form['password']).hexdigest()
    }
    value = mysql.query_db(query, data)

    # print user_id
    if len(value)==0:
        flash("Invalid email or password")
        session['loggedin'] = False
        return redirect('/')
    else:
        session['user_id'] = mysql.query_db(get_id, data)[0]['user_id']
        session['loggedin'] = True
        # session['loggedin'] = { True, user_id }

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

@app.route('/wall', methods = ['GET','POST'])
def wall():
    print session['loggedin']
    print request.method
    if session['loggedin'] == True or request.method == 'GET' or request.method == 'POST':
        # and request.method =='POST'
        query = "SELECT * FROM users WHERE users.user_id = :user_id"

        data = { 'user_id':session['user_id'] }
        first_name = mysql.query_db(query, data)[0]['first_name']




        message = mysql.query_db("SELECT m.message_id, m.message, m.created_at, concat(first_name,' ', last_name) as user from messages m join users u where m.user_id = u.user_id ORDER BY message_id desc")

        # comment = mysql.query_db("SELECT c.comment_id, u.user_id, c.message_id, c.comment, c.created_at, concat(first_name,' ', last_name) as user from comments c join users u where c.user_id=u.user_id order by comment_id desc")
        comment = mysql.query_db("SELECT c.comment_id, c.message_id, c.comment, c.created_at, concat(first_name,' ', last_name) as user from comments c join users u where c.user_id = u.user_id ORDER BY comment_id asc")
        # comment = mysql.query_db("SELECT comment, comments.created_at, CONCAT(users.first_name,' ', users.last_name) as user, message_id FROM comments JOIN users ON comments.user_id = users.user_id ORDER BY comments.created_at")
        print ("******* message *********")
        print message
        print ("******* COMMENT *********")
        print comment
        user_id = session['user_id']
        print user_id



    else:
        flash("not logged in")
        return render_template('index.html', all_messages=message, all_comment=comment, loggedin=session['loggedin'])



    return render_template('wall.html',all_messages=message, all_comments=comment, first_name=first_name, loggedin=session['loggedin'])


@app.route('/wall/message', methods=['POST'])
def messages():
    user_id = session['user_id']
    message_post = request.form['message_area']

    query = "INSERT INTO messages (message, created_at, updated_at, user_id) values (:message, NOW(), NOW(), :user_id)"
    query_data = { 'message': message_post, 'user_id':user_id}



    user_id = mysql.query_db(query, query_data)
    print user_id
        # insert comment here
    return redirect('/wall')

@app.route('/wall/comment/<message_id>', methods=['POST'])
def comment(message_id):
    user_id = session['user_id']
    print "MADE IT TO COMMENTS"
    print  message_id
    query = "INSERT INTO comments (comment, created_at, updated_at,message_id, user_id) VALUES (:comment, Now(), Now(), :message_id,:user_id)"
    data = {
        'comment': request.form['comment'],
        'user_id': session['user_id'],
        'message_id': message_id
    }
    comment_in = mysql.query_db(query, data)
    print comment_in
    return redirect('/wall')

@app.route('/signout',methods= ['POST'])
def sign_out():
    # button = request.form['button']
    # session['counter']=0
    session.pop('loggedin', None)
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
        user_id = mysql.query_db(insert_query, query_data)
        flash("success!!")
        session['user_id'] = user_id
        session['loggedin'] = True

        return redirect('/')

    return render_template('index.html', user_info=session['loggedin'])


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
