from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'fdwejdfsi243f45kjvid5lkdfi4jguie'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:root123@localhost:5432/blogs'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from blogs import routes
