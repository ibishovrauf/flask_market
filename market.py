from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request
from sqlalchemy import create_engine

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/hhhhh'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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
    userItem = db.Column(db.Integer, db.ForeignKey('item.id'))




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
    app.run(debug=True)

