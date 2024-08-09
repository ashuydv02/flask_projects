from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'fdwejdfsi243f45kjvid5lkdfi4jguie'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:root123@localhost:5432/blogs'
db = SQLAlchemy(app)

from blogs import routes
