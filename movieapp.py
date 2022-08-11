
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

# posts = [
#     {
#         'author': 'Corey Schafer',
#         'title': 'Game of Thrones',
#         'content': 'First post content',
#         'release_date': '2011-04-17',
#         'poster': 'https://cdn.watchmode.com/posters/0345534_poster_w185.jpg',
#         'Trailer': ' https://www.youtube.com/watch?v=BpJYNVhGf1s',
#         'streaming_links': 'https://tv.apple.com/us/episode/winter-is-coming/umc.cmc.11q7jp45c84lp6d16zdhum6ul?playableId=tvs.sbd.9001%3A494877461&showId=umc.cmc.7htjb4sh74ynzxavta5boxuzq'
#     }]




# @login_manager.user_loader
# def loading_user(username):
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     #cursor.execute('SELECT * FROM movie WHERE id = %s'(id))
#     cursor.execute(f"SELECT username FROM movies WHERE username = {username}")
#     # data = (id,)
#     # cursor.execute(query, data)
#     post = cursor.fetchone()
#     return post

# Homepage 
@app.route('/')
@app.route('/home')
def home():
    return render_template('home2.html')


# # Movie Page
# @app.route('/movie')
# def movie():
    
#     return render_template('movie2.html', posts=posts, title="Movie")


#movie details  
@app.route("/movie/title/<id>", methods=['GET'])
def movie(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #cursor.execute('SELECT * FROM movie WHERE id = %s'(id))
    cursor.execute(f"SELECT * FROM movies WHERE id = {id}")
    # data = (id,)
    # cursor.execute(query, data)
    current_post = cursor.fetchone()
    print(current_post)
    
    cursor.execute(f"SELECT * FROM StreamingService WHERE movie_id = {id}")
    # data = (id,)
    # cursor.execute(query, data)
    stream = cursor.fetchone()
    print(stream)
    return render_template('movie2.html', title='Movie', current_post=current_post, stream=stream) 





# Registration
@app.route('/register', methods =['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'fullname' in request.form:
        username = request.form['username']
        #password = request.form['password']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        fullname = request.form['fullname']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE username = % s', (username, ))
        account = cursor.fetchone()
        #find_user()
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
    # if form.validate_on_submit():
    #     username = request.form['username']
    #     password = request.form['password']
        
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username_new = request.form['username']
        print(username_new)
        password = request.form['password']
        print(password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #cursor.execute('SELECT * FROM Users WHERE username = % s AND password = % s', (username, password))
        # cursor.execute('SELECT * FROM Users WHERE username = %s AND password = %s', (username, password))
        cursor.execute('SELECT * FROM Users WHERE username = %s', [username_new])
        #cursor.execute(f"SELECT * FROM Users WHERE username = {username}")
        account_login = cursor.fetchone()
        print(account_login)
        account_password = account_login["password"]
        print(account_password)
        #if account:
        unhash_password = bcrypt.check_password_hash(account_password, password)
        print(unhash_password)
        if unhash_password:
            #login_user(user, remember=form.remember.data) #login user and remember data of user
            # next_page = request.args.get('next')
            # return redirect(next_page) if next_page else redirect(url_for('user'))
            return redirect(url_for('user', username_new=username_new))
        else:
            flash(f'Incorrect username / password !', 'danger')
    return render_template('login2.html', title='Login', form=form)


#route for logout page
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


# search page
@app.route("/search", methods=['GET', 'POST'])
def search():
    form = PostForm()
    if request.method == 'POST' and 'title' in request.form:
        converted_search = request.form['title']
        url0 = f"https://api.watchmode.com/v1/search/?apiKey={api_key}&search_field=name&search_value={converted_search}"
        movie_id = get_movie_id(url0)
        url1 = f"https://api.watchmode.com/v1/title/{movie_id}/details/?apiKey={api_key}&append_to_response=sources"
        #get_show_info(url1)
        results = get_show_info(url1)
        change = tuple(results)
        print(change)
        #print(results)
        # id = results[0]
        # title = results[1]
        # year=results[2] 
        # genre=results[3]
        # user_rating=results[4]
        # poster = results[5]
        # original_language=results[6]
        # trailer=results[7]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #for i in results:
            #cursor.execute("INSERT INTO Movies VALUES ('%s')", (i,))
    
        query = "INSERT INTO movies (id, title, year, genre, user_rating, poster, original_language, trailer) VALUES (% s, % s, % s, % s, % s, % s, % s, % s)" 
        cursor.execute(query, change)
        #mysql.connection.commit()
        
        #stream = type(streaming_links)
        #query2 = "INSERT INTO StreamingService (movie_id, service1, service2, service3, service4, service5, service6, service7, service8, service9) VALUES ((select id from movies), % s, % s, % s, % s, % s, % s, % s, % s, % s)"
        #query2 = "INSERT INTO StreamingService set (movie_id = (select id from movies), service1 = % s, service2 = % s, service3 = % s, service4 = % s, service5 = % s, service6 = % s, service7 = % s, service8 = % s, service9 = % s)" 
        # small_set = set(itertools.islice(streaming_links, 5))
        # print(small_set)
        small_set = set(itertools.islice(streaming_links, 5))
        print(small_set)
        small = tuple(small_set)
        print(small)
        query2 = "INSERT INTO StreamingService (movie_id, service1, service2, service3, service4, service5) VALUES ((select id from movies), % s, % s, % s, % s, % s)"
        cursor.execute(query2, small)
        #     row = (row,)
        #     print(row)
        #save_data(change)
        #cursor.execute("INSERT INTO movies (id, title, year, genre, user_rating, poster, original_language, trailer) VALUES (% s, % s, % s, % s, % s, % s, % s, % s)", % change)
        mysql.connection.commit()
        return redirect(url_for('movie'))
        #save_data(id, title, year, genre, user_rating, poster, original_language, trailer)
        #from movie_utils import Show
        #user_results = Show(results)
        #print(user_results)
        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #cursor.execute('INSERT INTO Movies VALUES (% s, % s, % s, % s, % s, % s, % s)', (id, title, year, genre, user_rating, poster, language, trailer,))
        #cursor.execute("""INSERT INTO Movies (id, title, release_year, genre, user_rating, poster, language, trailer) """ 
                       #""" VALUES (% s, % s, % s, % s, % s, % s, % s) """, (id, title, release_year, genre, user_rating, poster, language, trailer))
        # for i in results:
        #     cursor.execute("INSERT INTO Movies VALUES ('%s')", (i,))
        #mysql.connection.commit()
      
        #response = requests.get(url0)
        #show = response.json()
        #movie_id = show["title_results"][0]["id"]
        #print(f'Movie ID retrieved:{movie_id}')
    return render_template('search_movie.html', title='Search', form=form)
    




# #adding a picture to profile 
# def save_pic(form_pic):
#     random_hex = secrets.token_hex(8)
#     _, f_ext = os.path.splitext(form_pic.filename)
#     pic_fn = random_hex + f_ext
#     pic_path = os.path.join(app.root_path,'static/images_thesis', pic_fn)
#     #image resize - taken from https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog
#     output_size = (125, 125)  
#     i = Image.open(form_pic)
#     i.thumbnail(output_size)
#     i.save(pic_path)
    
    #return pic_fn
    
    
@login_manager.user_loader   
def load_user(username):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #cursor.execute('SELECT * FROM users WHERE username = % s', (username))
    cursor.execute(f"SELECT * FROM users WHERE username = {username}")
    user_account = cursor.fetchone()
    return user_account

@app.route("/user/<username_new>", methods=['GET']) #methods used to update account info if necessary
#@login_required
def user(username_new):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #cursor.execute(f"SELECT * FROM users WHERE username = {username}")
    #cursor.execute("SELECT * FROM users WHERE username = %s", (username_new))
    cursor.execute( "SELECT * FROM users WHERE username LIKE %s", [username_new] )
    #cursor.execute('SELECT * FROM Users WHERE username = %s', [username])
    #cursor.execute(f"SELECT * FROM Users WHERE username = {username}")
    profile_post = cursor.fetchone()
    print(profile_post)
    cursor.execute( "SELECT * FROM watchedmovies WHERE username LIKE %s", [username_new] )
    watched_post = cursor.fetchone()
    print(watched_post)
    
    cursor.execute( "SELECT * FROM savedmovies WHERE username LIKE %s", [username_new] )
    saved_post = cursor.fetchone()
    print(saved_post)
    return render_template('user2.html', title='User', profile_post=profile_post, watched_post=watched_post, saved_post=saved_post)


# watched buttons
@app.route("/movie/<id>/<username_new>/watched", methods=['GET']) #methods used to update account info if necessary
#@login_required
def watched(id, username_new):
    print(id)
    print(username_new)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT * FROM movies WHERE id = {id}")
    current_post = cursor.fetchone()
    watched_title = current_post["title"]
    print(watched_title)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO watchedmovies VALUES (% s, % s, % s)', (username_new, id, watched_title))
    mysql.connection.commit()
    flash('This movie has been saved to your watched list!', 'success')
    return redirect(url_for('user', id=id, username_new=username_new, current_post=current_post))

# save for later button
@app.route("/movie/<id>/<username_new>/save", methods=['GET']) #methods used to update account info if necessary
#@login_required
def save(id, username_new):
    print(id)
    print(username_new)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT * FROM movies WHERE id = {id}")
    current_post_new = cursor.fetchone()
    saved_title = current_post_new["title"]
    print(saved_title)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO savedmovies VALUES (% s, % s, % s)', (username_new, id, saved_title))
    mysql.connection.commit()
    flash('This movie has been saved to your save list!', 'success')
    return redirect(url_for('user', id=id, username_new=username_new, current_post_new=current_post_new))



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