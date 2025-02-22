"""Docstring"""
import cloudinary
import cloudinary.uploader

from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user, login_required, LoginManager, logout_user
from flask_login import UserMixin
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import ForeignKey, Integer, Column, String, Boolean
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:passmysql@localhost/market'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/market'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "test123test"
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
db = SQLAlchemy(app)


cloud_name = "rauf2"
api_key = "494188146737927"
api_secret = "73oXW8mcSLuJoxZdWxcaItSM-rY"

cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret,
)


@login_manager.user_loader
def load_user(user_id):
    """docstring"""
    return User.query.get(int(user_id))


class Item(db.Model):
    """docstring"""
    __tablename__ = 'item'
    __searchable__ = ['name', 'description']
    id = Column(Integer(), primary_key=True)
    name = Column(String(length=30), nullable=False)
    price = Column(Integer(), nullable=False)
    barcode = Column(String(length=12), nullable=False, unique=True)
    description = Column(String(length=1024), nullable=False)
    photo = Column(String(length=1024), nullable=False)
    user_id = Column(Integer(), ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="item")
    basket_id = Column(Integer, ForeignKey('basket.id'))


class User(db.Model, UserMixin):
    """docstring"""
    __tablename__ = 'user'
    id = Column(Integer(), primary_key=True)
    firstname = Column(String(length=30), nullable=False)
    lastname = Column(String(length=30), nullable=False)
    email = Column(String(length=50), nullable=False)
    username = Column(String(length=40), nullable=False)
    photo = Column(String(length=1024), nullable=True)
    password = Column(String(length=1024), nullable=False)
    admin = Column(Boolean, default=False)
    item = relationship("Item", back_populates="user")


class Basket(db.Model):
    """docstring"""
    __tablename__ = 'basket'
    id = Column(Integer(), primary_key=True)
    basket_user_id = Column(Integer, ForeignKey('user.id'), unique=True)
    users = relationship("User", backref=backref("basket", uselist=False))
    items = relationship("Item")


class BasketView(ModelView):
    """docstring"""
    can_delete = False  # disable user  deletion
    can_edit = False  # disable user  edition
    can_create = False  # disable user creation
    column_list = ['users', 'items']


class ItemView(ModelView):
    """docstring"""
    edit_template = 'edit_item.html'
    create_template = 'create_item.html'
    can_delete = False  # disable model deletion
    can_edit = False  # disable model edition
    page_size = 10
    column_exclude_list = ['photo', ]

    @expose('/new/', methods=['POST'])
    def create_view(self):
        """
            Custom create view.
        """

        item_name = request.form['ItemName']
        price = request.form['Price']
        barcode = request.form['Barcode']
        description = request.form['Description']
        file = request.files['file']
        upload_result = cloudinary.uploader.upload(file)
        photo_url = upload_result["secure_url"]
        item = Item(name=item_name, price=price, barcode=barcode, description=description,
                    photo=photo_url, user_id=current_user.id)
        item__name = Item.query.filter_by(name=item_name, user_id=current_user.id).first()
        barcode_1 = Item.query.filter_by(barcode=barcode).first()
        db.session.add(item)
        db.session.commit()
#        item_search = Item.query.filter_by(barcode=barcode).first()

        if item__name:
            flash('Item is already added', category='error')
        elif barcode_1:
            flash('This Barcode is already exists', category='error')
        else:
            flash('Item is added successfully!', category="success")

        return self.render('create_item.html')

    @expose('/new/', methods=['GET'])
    def create_view_get(self):
        """Docstring"""
        return self.render('create_item.html')


class UserView(ModelView):
    """docstring"""
    create_template = "create_user.html"
    page_size = 10
    column_exclude_list = ['photo', 'password', ]

    @expose('/new/', methods=["POST"])
    def create_app(self):
        """docstring"""
        enter = request.form.get('admin')
        if enter == "admin":
            admin_o = True
        else:
            admin_o = False
        first_name = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
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
            user = User(firstname=first_name, username=username, lastname=lastname,
                        email=email, admin = admin_o, password=hashed)
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            if admin_o is False:
                user_cart = Basket(basket_user_id=user_id)
                db.session.add(user_cart)
                db.session.commit()
            login_user(user, remember=True)
            flash('Account created!', category='success')
        return self.render('create_user.html')

    @expose('/new/', methods=["GET"])
    def create_new_user_get(self):
        """docstring"""
        return self.render('create_user.html')


class MyAdminIndexView(AdminIndexView):
    """docstring"""
    def is_accessible(self):
        """docstring"""
        if current_user.admin is True:
            return current_user.is_authenticated
        return flash("YOU ARE NOT ADMIN", category = 'error')


admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(UserView(User, db.session))
admin.add_view(ItemView(Item, db.session))
admin.add_view(BasketView(Basket, db.session))


@app.route('/')
@app.route('/home')
def home_page():
    """docstring"""
    return render_template('home.html')


@app.route('/sign-up', methods=['POST'])
def sign_up():
    """docstring"""
    first_name = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    username = request.form['username']
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
        user = User(firstname=first_name, username=username, lastname=lastname,
                    email=email, password=hashed)
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        user_cart = Basket(basket_user_id=user_id)
        db.session.add(user_cart)
        db.session.commit()
        login_user(user, remember=True)
        flash('Account created!', category='success')
        return redirect(url_for('login'))
    return render_template("register.html", user=current_user)


@app.route('/sign-up', methods=['GET'])
def sign_up_get():
    """docstring"""
    if current_user.is_authenticated:
        flash("You have already logged in, logout if you want", category="error")
        return redirect(url_for('profile'))
    return render_template('register.html')


@app.route('/login', methods=["GET"])
def login():
    """docstring"""
    if current_user.is_authenticated:
        flash("You have already logged in, logout if you want", category="error")
        return redirect(url_for('profile'))
    return render_template('login.html')


@app.route('/login', methods=["POST"])
def login_gh():
    """docstring"""
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user:
        if check_password_hash(user.password, password):
            flash('Logged in successfully!', category="success")
            login_user(user, remember=True)
            return redirect(url_for('profile'))
            # return render_template("login.html", user=current_user.id)
        flash('Incorrect password, try again.', category='error')
    if not user:
        flash('Username not exist.', category='error')
    return render_template("login.html")


@app.route('/profile')
@login_required
def profile():
    """docstring"""
    if current_user.is_authenticated:
        return render_template('profile.html', user=current_user)
    return render_template(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    """docstring"""
    logout_user()
    return redirect(url_for('home_page'))


@app.route('/items/<item_id>', methods=['GET'])
def show_item(item_id):
    """docstring"""
    item = Item.query.filter_by(id=item_id).first()
    user_id = item.user_id
    user = User.query.filter_by(id=user_id).first()
    return render_template('item.html', item=item, user=user)


@app.route('/items/<item_id>', methods=['POST'])
def show_item_post(item_id):
    """docstring"""
    if current_user.is_authenticated:
        item = Item.query.filter_by(id=item_id).first()
        user_cart = Basket.query.filter_by(basket_user_id=current_user.id).first()
        item_is_exist = 0
        for i in user_cart.items:
            if i == item:
                item_is_exist = 1
        if len(user_cart.items) > 50:
            flash("Your basket is overflowing", category='error')
        elif item_is_exist == 1:
            flash("This item is exist", category='error')
        else:
            user_cart.items.append(item)
            db.session.commit()
        return redirect(url_for('show_item', item_id=item_id))
    flash("First you must login", category="error")
    return redirect(url_for('login'))


@app.route('/basket', methods=['GET'])
def basket():
    """docstring"""
    if current_user.admin is True:
        return redirect(url_for('profile'))
    user_cart = Basket.query.filter_by(basket_user_id=current_user.id).first()
    item = user_cart.items
    total_price = 0
    if total_price == 0:
        for items in item:
            total_price += items.price
    return render_template("basket.html", item=item, price=total_price)


@app.route('/basket', methods=['POST'])
def basket_delete():
    """docstring"""
    item = request.form['item']
    item = Item.query.filter_by(id=item).first()
    user_cart = Basket.query.filter_by(basket_user_id=current_user.id).first()
    user_cart.items.remove(item)
    db.session.commit()
    user_cart = Basket.query.filter_by(basket_user_id=current_user.id).first()
    return render_template("basket.html", item=user_cart.items)


@app.route('/profile/redact-profile', methods=["GET"])
def redact_profile():
    """docstring"""
    return render_template('redact_profile.html', user=current_user)


@app.route('/profile/redact-profile', methods=['POST'])
def redact_profile_post():
    """docstring"""
    first_name = request.form['firstname']
    lastname = request.form['lastname']
    username = request.form['username']
    file = request.files['file']
    if first_name != current_user.firstname:
        db.session.current_user.firstname = first_name
    if lastname != current_user.lastname:
        current_user.lastname = lastname
    if username != current_user.username:
        current_user.username = username
    if file.filename != "":
        upload_result = cloudinary.uploader.upload(file)
        photo_url = upload_result["secure_url"]
        current_user.photo = photo_url
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/profile/my-items')
def my_items():
    """docstring"""
    if current_user.admin is True:
        page = request.args.get('page', 1, type=int)
        items = Item.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=3)

        return render_template("users_item.html", item=items)
    return render_template("404.html")


@app.route('/my_items/search', methods=['POST'])
def my_items_search():
    """docstring"""
    search1 = request.form["search"]
    if not search1:
        search1 = "wrong search"
    order1 = "up_price"
    return redirect(url_for('my_items_search_results', query=search1, order=order1))


@app.route('/search/vs', methods=['POST'])
def search_order_my_items():
    """docstring"""
    value = request.form.get('thing')
    val = value.split(",")
    return redirect(url_for('my_items_search_results', query=val[1], order=val[0]))


@app.route('/my_items/<query>/<order>')
def my_items_search_results(query, order):
    """docstring"""
    page = request.args.get('page', 1, type=int)
    if order == "up_price":
        items = Item.query.order_by(Item.price.desc())\
                          .filter(Item.name.contains(query) | Item.description.contains(query))\
                          .filter_by(user_id=current_user.id)\
                          .paginate(page=page, per_page=3)
    elif order == "barcode":
        items = Item.query.order_by(Item.barcode.desc()) \
                          .filter(Item.name.contains(query) | Item.description.contains(query))\
                          .filter_by(user_id=current_user.id)\
                          .paginate(page=page, per_page=3)
    elif order == "name":
        items = Item.query.order_by(Item.name.desc())\
            .filter(Item.name.contains(query) | Item.description.contains(query)) \
            .filter_by(user_id=current_user.id)\
            .paginate(page=page, per_page=3)
    return render_template('users_item_result.html', items=items, query=query, thing=order)


@app.route('/items', methods=['GET'])
def all_items():
    """docstring"""
    page = request.args.get('page', 1, type=int)
    items = Item.query.paginate(page=page, per_page=3)
    return render_template('items_page.html', items=items)


@app.route('/items/order-by', methods=['POST'])
def ordered_items():
    """docstring"""
    value = request.form.get('thing')
    page = request.args.get('page', 1, type=int)
    if value == "name":
        items = Item.query.order_by(Item.name.desc()).paginate(page=page, per_page=3)
    elif value == "barcode":
        items = Item.query.order_by(Item.barcode.desc()).paginate(page=page, per_page=3)
    elif value == "up_price":
        items = Item.query.order_by(Item.price.desc()).paginate(page=page, per_page=3)
    return render_template('items_page.html', items=items, thing=value)


@app.route('/search/v', methods=['POST'])
def search_order():
    """docstring"""
    value = request.form.get('thing')
    val = value.split(",")
    return redirect(url_for('search_results', query=val[1], order=val[0]))


@app.route('/search', methods=['POST'])
def search():
    """docstring"""
    search1 = request.form["search"]
    if not search1:
        search1 = "wrong search"
    order1 = "up_price"
    return redirect(url_for('search_results', query=search1, order=order1))


@app.route('/search_results/<query>/<order>')
def search_results(query, order):
    """docstring"""
    page = request.args.get('page', 1, type=int)
    if order == "up_price":
        items = Item.query.order_by(Item.price.desc())\
                          .filter(Item.name.contains(query) | Item.description.contains(query))\
                          .paginate(page=page, per_page=3)
    elif order == "barcode":
        items = Item.query.order_by(Item.barcode.desc()) \
                          .filter(Item.name.contains(query) | Item.description.contains(query)) \
                          .paginate(page=page, per_page=3)
    elif order == "name":
        items = Item.query.order_by(Item.name.desc()) \
            .filter(Item.name.contains(query) | Item.description.contains(query)) \
            .paginate(page=page, per_page=3)
    return render_template('search_results.html', items=items, query=query, thing=order)


@app.route('/delete/<item_id>', methods=['POST'])
def delete_item(item_id):
    item = Item.query.filter_by(id=item_id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('home_page'))


if __name__ == "__main__":
    app.run(debug=True)
