from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ---------------- USER ----------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')

    # Relationships
    meals = db.relationship('Meal', backref='cook', lazy=True)
    houses = db.relationship('House', backref='owner', lazy=True)


# ---------------- HOUSE ----------------
class House(db.Model):
    __tablename__ = 'houses'
    id = db.Column(db.Integer, primary_key=True)

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    address = db.Column(db.Text)
    city = db.Column(db.String(100))

    breakfast_time = db.Column(db.String(50))
    lunch_time = db.Column(db.String(50))
    dinner_time = db.Column(db.String(50))
    pickup_time = db.Column(db.String(50))

    # Relationships
    meals = db.relationship('Meal', backref='house', lazy=True)
    images = db.relationship('HouseImage', backref='house', lazy=True)


# ---------------- HOUSE IMAGES ----------------
class HouseImage(db.Model):
    __tablename__ = 'house_images'
    id = db.Column(db.Integer, primary_key=True)

    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'))
    image = db.Column(db.String(200))


# ---------------- MEAL ----------------
class Meal(db.Model):
    __tablename__ = 'meals'

    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=True)
    cook_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Food info
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    portions = db.Column(db.Integer, nullable=False)
    available_till = db.Column(db.DateTime, nullable=True)

    # Food details
    food_type = db.Column(db.String(20), nullable=False)
    packaging = db.Column(db.String(100), nullable=True)
    allergies = db.Column(db.String(255), nullable=True)
    ingredients = db.Column(db.Text, nullable=True)

    # Relationships
    meal_requests = db.relationship('MealRequest', back_populates='meal', lazy=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)



# ---------------- MEAL REQUEST ----------------
class MealRequest(db.Model):
    __tablename__ = 'meal_requests'

    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    status = db.Column(db.String(20), default='pending')
    pickup_date = db.Column(db.Date)
    pickup_time = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    requester = db.relationship('User', backref='meal_requests')
    meal = db.relationship('Meal', back_populates='meal_requests')

