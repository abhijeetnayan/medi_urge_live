from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Hospital(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String(150), nullable=False)
    # address = db.Column(db.String(255), nullable=False)
    # latitude = db.Column(db.Float, nullable=False)
    # longitude = db.Column(db.Float, nullable=False)
    # contact_number = db.Column(db.String(20))
    # is_verified = db.Column(db.Boolean, default=True)
    # last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # resources = db.relationship('Resource', backref='hospital', lazy=True)


    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True) # For hospital login
    password = db.Column(db.String(255))
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    hosp_type = db.Column(db.String(20)) # 'Government' or 'Private'
    description = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False) # Admin sets this to True
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    resources = db.relationship('Resource', backref='hospital', lazy=True)
    requests = db.relationship('ResourceRequest', backref='hospital', lazy=True) 

class Resource(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    # hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    # resource_type = db.Column(db.String(50), nullable=False) # e.g., 'ICU Bed', 'Ventilator', 'Oxygen'
    # total_capacity = db.Column(db.Integer, default=0)
    # available_count = db.Column(db.Integer, default=0)


    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    resource_type = db.Column(db.String(50)) # "ICU Bed", "General Bed", "Ventilator"
    available = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0.0)




class ResourceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(10), unique=True, nullable=False)
    user_mobile = db.Column(db.String(15), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    status = db.Column(db.String(20), default='Pending') # Pending, Accepted, Denied
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)





class BlockedUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.String(15), unique=True, nullable=False)
    reason = db.Column(db.String(255))
    reported_by = db.Column(db.Integer, db.ForeignKey('hospital.id')) # Which hospital flagged them
    is_blocked = db.Column(db.Boolean, default=False) # False = Pending Admin Review
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)