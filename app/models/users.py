from datetime import datetime
from app.extensions import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    biography = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(255), nullable=True)
    contact = db.Column(db.String(20), unique=True, nullable=False)
    gender = db.Column(db.String(20), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), default="user")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

  
    # Password helpers
  
    def set_password(self, raw_password):
        self.password = bcrypt.generate_password_hash(
            raw_password
        ).decode("utf-8")

    def check_password(self, password_input):
        return bcrypt.check_password_hash(self.password, password_input)

    
    def __repr__(self):
        return f"<User {self.email}>"