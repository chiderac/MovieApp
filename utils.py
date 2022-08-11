from flask import Flask
#from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message ='You must be logged in to access this page'
login_manager.login_message_category = 'info'