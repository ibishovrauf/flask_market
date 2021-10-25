import os

from flask_login import UserMixin, login_user, current_user, login_required, LoginManager, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import backref

eng = 'mysql://root:root@localhost/market'
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:passmysql@localhost/market'
app.config['SQLALCHEMY_DATABASE_URI'] = eng
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "test123test"
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


db = SQLAlchemy(app)
admin = Admin(app)


class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=124), nullable=False, unique=True)
    user_id = db.Column(db.Integer(), ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="item")
    basket_id = db.Column(db.Integer, ForeignKey('basket.id'))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(length=30), nullable=False)
    lastname = db.Column(db.String(length=30), nullable=False)
    email = db.Column(db.String(length=50), nullable=False)
    rights = db.Column(db.String(length=10), nullable=False)
    password = db.Column(db.String(length=124), nullable=False)
    item = relationship("Item", back_populates="user")


class Basket(db.Model):
    __tablename__ = 'basket'
    id = db.Column(db.Integer(), primary_key=True)
    basket_user_id = db.Column(db.Integer, ForeignKey('user.id'), unique=True)
    users = relationship("User", backref=backref("basket", uselist=False))
    items = relationship("Item")


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Item, db.session))
admin.add_view(ModelView(Basket, db.session))


@app.route('/')
@app.route('/home')
def home_page():
    items = Item.query.all()
    return render_template('home.html', items=items)


@app.route('/about', defaults={"item": Item.name})
@app.route('/about/<item>')
def about_item(item):
    return render_template("about.html", item=item)


@app.route('/sign-up', methods=['POST'])
def sign_up():
    first_name = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    rights = request.form.get('thing', '')
    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email already exists.', category='error')
    elif len(email) < 4:
        flash('Email must be greater than 3 characters.', category='error')
    elif len(first_name) < 2:
        flash('First name must be greater than 1 character.', category='error')
    elif len(password) < 7:
        flash('Password must be at least 7 characters.', category='error')
    else:
        hashed = generate_password_hash(password, method="sha256")
        user = User(firstname=first_name, lastname=lastname, email=email, rights=rights , password=hashed)
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        basket = Basket(basket_user_id=user_id)
        db.session.add(basket)
        db.session.commit()
        login_user(user, remember=True)
        flash('Account created!', category='success')
        return redirect(url_for('login'))
    return render_template("register.html", user=current_user)


@app.route('/sign-up', methods=['GET'])
def sign_up_get():
    return render_template('register.html')


@app.route('/login', methods=["GET"])
def login():
    return render_template('login.html')


@app.route('/login', methods=["POST"])
def login_gh():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()
    if user:
        if check_password_hash(user.password, password):
            flash('Logged in successfully!', category="success")
            login_user(user, remember=True)
            return redirect(url_for('profile'))
        else:
                flash('Incorrect password, try again.', category='error')
    else:
        flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user.id)


@app.route('/profile/')
@login_required
def profile():
    if current_user:
        return render_template('profile.html', user=current_user)
    else:
        return render_template(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_page'))


if __name__ == "__main__":
    app.run(debug=True)

