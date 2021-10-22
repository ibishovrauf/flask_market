import os

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:passmysql@localhost/market'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/market'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "test123test"

db = SQLAlchemy(app)
admin = Admin(app)
Base = declarative_base()



class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=124), nullable=False, unique=True)
    user_id = db.Column(db.Integer(), ForeignKey("user.id"), nullable = False)
    user = relationship("User", back_populates="item")
    basket = relationship("Basket", back_populates="item")

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(length=30), nullable=False)
    lastname = db.Column(db.String(length=30), nullable=False)
    email = db.Column(db.String(length=50), nullable=False)
    password = db.Column(db.String(length=124), nullable=False)
    item = relationship("Item", back_populates="user")
    basket = relationship("Basket", back_populates="user")


class Basket(db.Model):
    __tablename__ = 'basket'
    id = db.Column(db.Integer(), primary_key=True)
    user_basket_id = db.Column(db.Integer(), ForeignKey("user.id"))
    item_basket_id = db.Column(db.Integer(), ForeignKey("item.id"))
    user = relationship("User", back_populates="basket")
    item = relationship("Item", back_populates="basket")


#
# class Basket(db.Model):
#     id = db.Column(db.Integer(), primary_key=True)
#     user_id = db.Column(db.Integer(), ForeignKey('User.id'))
#     item_id = db.Column(db.Integer(), ForeignKey('Item.id'))


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Item, db.session))
admin.add_view(ModelView(Basket, db.session))


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/login')
def login():

    return render_template('login.html')


@app.route('/sign-up', methods=['POST'])
def sign_up():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']

    hashed = generate_password_hash(password, method="sha256")
    user = User(firstname=firstname, lastname=lastname, email=email, password=hashed)

    db.session.add(user)
    db.session.commit()
    return render_template('home.html')


@app.route('/sign-up', methods=['GET'])
def sign_up_get():
    return render_template('register.html')


# cloudinary.config(
#     cloud_name=os.getenv('rauf2'),
#     api_key=os.getenv('494188146737927'),
#     api_secret=os.getenv('73oXW8mcSLuJoxZdWxcaItSM-rY'))

if __name__ == "__main__":
    app.run(debug=True)

