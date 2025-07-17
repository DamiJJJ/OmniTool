from datetime import datetime
from extensions import db

class CurrencyLog(db.Model):
    """
    Database model to log Currency conversion operations.
    """
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    from_currency = db.Column(db.String(10), nullable=False)
    to_currency = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    converted_amount = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<CurrencyLog {self.id} - {self.from_currency} to {self.to_currency}>'

class Todo(db.Model):
    """
    Database model for To-Do list tasks.
    """
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} - {self.description}>'