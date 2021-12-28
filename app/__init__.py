
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask

# 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
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:passmysql@localhost/market'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/market'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "test123test"
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
db = SQLAlchemy(app)

from app import routes