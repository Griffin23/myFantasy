from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.routing import BaseConverter

class RegexConverter(BaseConverter):
    def __init__(self, map, *args):
        self.map = map
        self.regex = args[0]

app = Flask(__name__)
app.url_map.converters['regex'] = RegexConverter
app.config.from_object('config')
app.secret_key = 'Th1S1sS3cR3tK3y4MyApP'
db = SQLAlchemy(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost:3306/test?charset=utf8mb4'
#app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

from app import views
