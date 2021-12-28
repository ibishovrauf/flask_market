from flask_login import UserMixin
from app import db


class Item(db.Model):
    """docstring"""
    __tablename__ = 'item'
    __searchable__ = ['name', 'description']
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=False)
    photo = db.Column(db.String(length=1024), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="item")
    basket_id = db.Column(db.Integer, db.ForeignKey('basket.id'))


class User(db.Model, UserMixin):
    """docstring"""
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(length=30), nullable=False)
    lastname = db.Column(db.String(length=30), nullable=False)
    email = db.Column(db.String(length=50), nullable=False)
    username = db.Column(db.String(length=40), nullable=False)
    photo = db.Column(db.String(length=1024), nullable=True)
    password = db.Column(db.String(length=1024), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    item = db.relationship("Item", back_populates="user")


class Basket(db.Model):
    """docstring"""
    __tablename__ = 'basket'
    id = db.Column(db.Integer(), primary_key=True)
    basket_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    users = db.relationship("User", backref=db.backref("basket", uselist=False))
    items = db.relationship("Item")
