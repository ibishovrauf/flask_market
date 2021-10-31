import cloudinary
import cloudinary.uploader
from flask_paginate import Pagination, get_page_args
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, current_user, login_required, LoginManager, logout_user
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import backref
import clodinary_config

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
    name = db.Column(db.String(length=30), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=False)
    photo = db.Column(db.String(length=1024), nullable=False)
    user_id = db.Column(db.Integer(), ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="item")
    basket_id = db.Column(db.Integer, ForeignKey('basket.id'))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(length=30), nullable=False)
    lastname = db.Column(db.String(length=30), nullable=False)
    email = db.Column(db.String(length=50), nullable=False)
    username = db.Column(db.String(length=40), nullable=False)
    photo = db.Column(db.String(length=1024), nullable=True)
    rights = db.Column(db.String(length=10), nullable=False)
    password = db.Column(db.String(length=1024), nullable=False)
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
    return render_template('home.html')


@app.route('/sign-up', methods=['POST'])
def sign_up():
    first_name = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    username = request.form['username']
    rights = request.form.get('thing', '')
    user = User.query.filter_by(email=email).first()
    user1 = User.query.filter_by(username=username).first()

    if user:
        flash('Email already exists.', category='error')
    elif user1:
        flash('username is exists', category="error")
    elif len(email) < 4:
        flash('Email must be greater than 3 characters.', category='error')
    elif len(first_name) < 2:
        flash('First name must be greater than 1 character.', category='error')
    elif len(password) < 7:
        flash('Password must be at least 7 characters.', category='error')
    else:
        hashed = generate_password_hash(password, method="sha256")
        user = User(firstname=first_name, username=username, lastname=lastname, email=email, rights=rights , password=hashed)
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
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
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


@app.route('/profile')
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


@app.route('/items/<item_id>', methods=['GET'])
def show_item(item_id):
    item = Item.query.filter_by(id=item_id).first()
    user_id = item.user_id
    user = User.query.filter_by(id=user_id).first()
    return render_template('item.html', item=item, user=user)


@app.route('/items', methods=['GET'])
def all_items():
    page = request.args.get('page', 1, type=int)
    items = Item.query.paginate(page=page, per_page=3)
    return render_template('items_page.html', items=items)


@app.route('/items', methods=['POST'])
def show_item_post():
    if current_user.is_authenticated:

        item = request.form['item']
        item = Item.query.filter_by(id=item).first()
        user_cart = Basket.query.filter_by(basket_user_id=current_user.id).first()
        for it in user_cart.items:
            if it == item:
                item_is_exist = 1
        if len(user_cart.items) > 50:
            flash("Your basket is overflowing", category='error')
        elif item_is_exist == 1:
            flash("This item is exist", category='error')
        else:
            user_cart.items.append(item)
            db.session.commit()

        return redirect(url_for('all_items'))
    else:
        flash("First you must login", category="error")
        return redirect(url_for('login'))


@app.route('/add_item', methods=['POST'])
def add_item():
    itemname = request.form['ItemName']
    price = request.form['Price']
    barcode = request.form['Barcode']
    description = request.form['Description']
    file = request.files['file']
    upload_result = cloudinary.uploader.upload(file)
    photo_url = upload_result["secure_url"]

    item = Item(name=itemname, price=price, barcode=barcode, description=description,photo = photo_url, user_id=current_user.id)
    item__name = Item.query.filter_by(name=itemname, user_id=current_user.id).first()
    barcode_1 = Item.query.filter_by(barcode=barcode).first()
    db.session.add(item)
    db.session.commit()
    if item__name:
        flash('Item is already added', category='error')
    elif barcode_1:
        flash('This Barcode is already exists', category='error')
    else:
        flash('Item is added successfully!', category="success")

    return render_template("add_item.html")


@app.route('/add_item', methods=['GET'])
def add_item_get():
    return render_template("add_item.html")


@app.route('/basket', methods=['GET'])
def basket():
    user_cart = Basket.query.filter_by(basket_user_id=current_user.id).first()
    item = user_cart.items
    return render_template("basket.html", item=item)


@app.route('/basket', methods=['POST'])
def basket_delete():
    item = request.form['item']
    item = Item.query.filter_by(id=item).first()
    user_cart = Basket.query.filter_by(basket_user_id=current_user.id).first()
    user_cart.items.remove(item)
    db.session.commit()
    user_cart = Basket.query.filter_by(basket_user_id=current_user.id).first()
    return render_template("basket.html", item=user_cart.items)


if __name__ == "__main__":
    app.run(debug=True)

