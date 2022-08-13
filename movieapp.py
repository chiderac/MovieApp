
from flask import Flask, render_template, url_for,  flash, redirect, request, redirect, url_for, session
from forms import RegistrationForm, LoginForm, PostForm
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from movie_utils import get_movie_id, get_show_info, get_links, api_key, streaming_links
from PIL import Image
import requests 
import json
import secrets
import os
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import MySQLdb.cursors
import mysql.connector
from sql_python_connection import save_data
import re
import itertools


app = Flask(__name__)



app.config['SECRET_KEY'] = '5ef125114dc5f9b1ba25242cfac67cc0'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = "Cecile060414"
app.config['MYSQL_DB'] = 'movieapp'

# Intialize MySQL
mysql = MySQL(app)


bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message ='You must be logged in to access this page'
login_manager.login_message_category = 'info'




# Homepage 
@app.route('/')
@app.route('/home')
def home():
    return render_template('home2.html')




#movie details  
@app.route("/movie/<id>", methods=['GET'])
#@login_required
def movie(id):
    print(id)
    username_new = session["username"]
    print(username_new)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT * FROM movies WHERE id = {id}")
    current_post = cursor.fetchone()
    print(current_post)
    
    cursor.execute(f"SELECT * FROM StreamingService WHERE movie_id = {id}")
    stream = cursor.fetchone()
    print(stream)
    del stream["movie_id"]
    print(stream)
    
    cursor.execute( "SELECT * FROM users WHERE username LIKE %s", [username_new] )
    profile_post = cursor.fetchone()
    print(profile_post)
    return render_template('movie2.html', title='Movie', current_post=current_post, stream=stream, id=id, profile_post=profile_post) 





# Registration
@app.route('/register', methods =['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'fullname' in request.form:
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        fullname = request.form['fullname']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
             flash(f'Account already exists !', 'danger') 
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash(f'Invalid email address !', 'danger') 
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash(f'Username must contain only characters and numbers !', 'danger')     
        elif not username or not password or not email:
            flash(f'Please fill out the form !', 'danger') 
        else:
            cursor.execute('INSERT INTO Users VALUES (% s, % s, % s, % s)', (username, fullname, email, password))
            mysql.connection.commit()
            flash(f'You have successfully registered !', 'success') 
            return redirect(url_for('login'))
    elif request.method == 'POST':
        flash(f'Please fill out the form !', 'danger') 
    return render_template('register2.html', form=form)


# login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username_new = request.form['username']
        print(username_new)
        password = request.form['password']
        print(password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE username = %s', [username_new])
        account_login = cursor.fetchone()
        if account_login:
            session['loggedin'] = True
            session['username'] = account_login['username']
            session['password'] = account_login['password']
            account_password = session['password']
            msg = 'Logged in successfully !'
            unhash_password = bcrypt.check_password_hash(account_password, password)
            print(unhash_password)
        if unhash_password:
            return redirect(url_for('user', username_new=username_new))
        else:
            flash(f'Incorrect username / password !', 'danger')
    return render_template('login2.html', title='Login', form=form)


#route for logout page
@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# search page
@app.route("/search", methods=['GET', 'POST'])
def search():
    form = PostForm()
    if request.method == 'POST' and 'title' in request.form:
        converted_search = request.form['title']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM movies WHERE title= % s', (converted_search, ))
        first = cursor.fetchone()
        print(first)
        
        if first:
            post_id = first["id"]
            print(post_id)
            cursor.execute('SELECT * FROM StreamingService WHERE movie_id = % s', (post_id,))
            second = cursor.fetchone()
            print(second)
            return redirect(url_for('movie', id=post_id))
        else:
            url0 = f"https://api.watchmode.com/v1/search/?apiKey={api_key}&search_field=name&search_value={converted_search}"
            movie_id = get_movie_id(url0)
            url1 = f"https://api.watchmode.com/v1/title/{movie_id}/details/?apiKey={api_key}&append_to_response=sources"
            results = get_show_info(url1)
            change = tuple(results)
            print(change)
            specific_id = change[0]
            print(specific_id)
        
            
            # insert into movies database 
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query = "INSERT INTO movies (id, title, year, genre, user_rating, poster, original_language, trailer) VALUES (% s, % s, % s, % s, % s, % s, % s, % s)" 
            cursor.execute(query, change)
            mysql.connection.commit()
            
            small_set = set(itertools.islice(streaming_links, 5))
            print(small_set)
            fixed = list(small_set)
            print(fixed)
            
            if len(fixed) < 5: 
            # Make a list of None, one per missing value
            # Add the None list to the list of values to make up the count.
                extras = [None] * (5 - len(small_set))
                print(extras)
                fixed.extend(extras)
            print(fixed)
            print("This is fixed", fixed)
            fixed.insert(0, specific_id)
            fixed_set = tuple(fixed)
            print(fixed_set)
            
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query2 = "INSERT INTO StreamingService (movie_id, service1, service2, service3, service4, service5) VALUES ((select id from movies WHERE id = %s), % s, % s, % s, % s, % s)"
            cursor.execute(query2, fixed_set)
            mysql.connection.commit()
            return redirect(url_for('movie', id=specific_id))
        
    return render_template('search_movie.html', title='Search', form=form)
    



    
# login manager - not used 
@login_manager.user_loader   
def load_user(username):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT * FROM users WHERE username = {username}")
    user_account = cursor.fetchone()
    return user_account


# user page
@app.route("/user/<username_new>", methods=['GET']) 
#@login_required
def user(username_new):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute( "SELECT * FROM users WHERE username LIKE %s", [username_new] )
    profile_post = cursor.fetchone()
    print(profile_post)
    
    cursor.execute( "SELECT * FROM watchedmovies WHERE username LIKE %s", [username_new] )
    watched_post_all = cursor.fetchall()
    print(watched_post_all)
    
    for watched_p in watched_post_all:
        watched_id = watched_p["movie_id"]
        print(watched_id)
    
    cursor.execute( "SELECT * FROM watchedmovies WHERE movie_id = %s", [watched_id] )
    watched = cursor.fetchone()
    print(watched)
    
    
    cursor.execute( "SELECT * FROM savedmovies WHERE username LIKE %s", [username_new] )
    saved_post_all = cursor.fetchall()
    print(saved_post_all)
    
    for saved_p in saved_post_all:
        saved_id = saved_p["movie_id"]
        print(saved_id)
    
    cursor.execute( "SELECT * FROM savedmovies WHERE movie_id = %s", [saved_id] )
    saved = cursor.fetchone()
    print(saved)
    
    return render_template('user2.html', title='User', profile_post=profile_post, watched_post_all=watched_post_all, saved_post_all=saved_post_all, watched=watched, saved=saved)


# watched buttons
@app.route("/movie/<id>/<username_new>/watched", methods=['GET']) 
#@login_required
def watched(id, username_new):
    print(id)
    username_new = session["username"]
    print(username_new)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT * FROM movies WHERE id = {id}")
    current_post = cursor.fetchone()
    watched_title = current_post["title"]
    print(watched_title)
    
    
    cursor.execute( "SELECT * FROM users WHERE username LIKE %s", [username_new] )
    profile_post = cursor.fetchone()
    print(profile_post)
    watched_username = profile_post["username"]
    print(watched_username)
    
   
    
    cursor.execute( "SELECT * FROM watchedmovies WHERE username = %s and movie_id = %s", (username_new, id))
    watched_post = cursor.fetchone()
    print(watched_post)
    message = ""
    if watched_post:
        message = "You have already saved this movie to your watched list!"
        print("You have already saved this movie to your watched list!")
        flash('You have already saved this movie to your watched list!', 'danger')
        return redirect(url_for('movie', id=id))
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO watchedmovies VALUES (% s, % s, % s)', (watched_username, id, watched_title))
        mysql.connection.commit()
        flash('This movie has been saved to your watched list!', 'success')
        message = 'This movie has been saved to your watched list!'
        print('This movie has been saved to your watched list!')
        cursor.execute( "SELECT * FROM watchedmovies WHERE username = %s", [username_new])
        watched_post_all = cursor.fetchall()
        print(watched_post_all)
    return redirect(url_for('user', id=id, username_new=username_new, current_post=current_post, profile_post=profile_post, watched_post=watched_post, message=message, watched_post_all=watched_post_all))

# save for later button
@app.route("/movie/<id>/<username_new>/save", methods=['GET']) 
#@login_required
def save(id, username_new):
    print(id)
    username_new = session["username"]
    print(username_new)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT * FROM movies WHERE id = {id}")
    current_post_new = cursor.fetchone()
    saved_title = current_post_new["title"]
    print(saved_title)
    
    
    cursor.execute( "SELECT * FROM users WHERE username LIKE %s", [username_new] )
    profile_post = cursor.fetchone()
    print(profile_post)
    saved_username = profile_post["username"]
    print(saved_username)
    
    cursor.execute( "SELECT * FROM savedmovies WHERE username = %s and movie_id=%s", (username_new, id) )
    saved_post = cursor.fetchone()
    print(saved_post)
    
    if saved_post:
        message = "You have already saved this movie to your save list!"
        print("You have already saved this movie to your save list!")
        flash('You have already saved this movie to your save list!', 'danger')
        return redirect(url_for('movie', id=id))
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO savedmovies VALUES (% s, % s, % s)', (saved_username, id, saved_title))
        mysql.connection.commit()
        flash('This movie has been saved to your save list!', 'success')
        message = 'This movie has been saved to your save list!'
        print('This movie has been saved to your save list!')
        cursor.execute( "SELECT * FROM savedmovies WHERE username = %s", [username_new])
        saved_post_all = cursor.fetchall()
        print(saved_post_all)
    return redirect(url_for('user', username_new=username_new, current_post_new=current_post_new, profile_post=profile_post, saved_post=saved_post, message=message, saved_post_all=saved_post_all))



#creating custom error pages for my application
@app.errorhandler(404)
def pagenotfound(e):
    return render_template('404.html'), 404

#internal server error
@app.errorhandler(500)
def pagenotfound(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(debug=True)