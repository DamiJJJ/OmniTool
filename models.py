from datetime import datetime
from extensions import db

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    currency_logs = db.relationship("CurrencyLog", backref="user", lazy=True)
    todos = db.relationship("Todo", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class CurrencyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    from_currency = db.Column(db.String(3), nullable=False)
    to_currency = db.Column(db.String(3), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    converted_amount = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CurrencyLog {self.from_currency} to {self.to_currency} by User {self.user_id}>"


class FavoriteCurrencyPair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    from_currency = db.Column(db.String(3), nullable=False)  # np. "USD"
    to_currency = db.Column(db.String(3), nullable=False)  # np. "EUR"

    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "from_currency", "to_currency", name="_user_currency_pair_uc"
        ),
    )

    def __repr__(self):
        return f"<FavoriteCurrencyPair User {self.user_id}: {self.from_currency}-{self.to_currency}>"


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    deadline = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Todo {self.id} for User {self.user_id}>"


class FavoriteWeatherLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    city_name = db.Column(db.String(100), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "city_name", name="_user_city_uc"),
    )

    def __repr__(self):
        return f"<FavoriteWeatherLocation {self.city_name} for User {self.user_id}>"
