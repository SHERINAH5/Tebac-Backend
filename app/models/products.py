from app.extensions import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  
    user = db.relationship("User", backref="products")
    name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=True)
    image = db.Column(db.String(255), nullable=True)  

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __init__(self, name, description, stock_quantity, user_id, price=None, image=None):
        self.name = name
        self.price = price
        self.description = description
        self.stock_quantity = stock_quantity
        self.user_id = user_id
        self.image = image

    def __repr__(self):
        return f"<Product {self.name}>"
