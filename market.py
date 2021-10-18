from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:passmysql@localhost/market'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "test123test"

db = SQLAlchemy(app)
admin = Admin(app)




class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=124), nullable=False, unique=True)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(length=30), nullable=False)
    lastname = db.Column(db.String(length=30), nullable=False)
    email = db.Column(db.String(length=50), nullable=False)
    password = db.Column(db.String(length=30), nullable=False)

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Item, db.session))



@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    if request.method == "POST":
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        user = User(firstname=firstname, lastname=lastname, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return render_template('register.html')
    else:
        return render_template('register.html')


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)

