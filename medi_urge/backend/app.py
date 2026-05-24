















import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Hospital, Resource, ResourceRequest, AuditLog, BlockedUser
import redis
import uuid
from datetime import datetime

# Initialize App
app = Flask(__name__)





# Grab the database URL from the environment, fallback to local SQLite
db_url = os.getenv('DATABASE_URL', 'sqlite:///medical_tracker.db')

# FIX FOR RENDER: SQLAlchemy 1.4+ requires 'postgresql://' but Render gives 'postgres://'
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)





# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medical_tracker.db'




app.config['SQLALCHEMY_DATABASE_URI'] = db_url



app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
db.init_app(app)

# # Initialize Redis (For 30-min Token Expiry)
# r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, db=0, decode_responses=True)

# Initialize Redis (For 30-min Token Expiry)
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
r = redis.Redis.from_url(redis_url, decode_responses=True)






# Try to import geo_utils, fallback if it doesn't exist yet
try:
    from geo_utils import sort_hospitals_by_proximity
except ImportError:
    def sort_hospitals_by_proximity(lat, lng, hospitals):
        return hospitals # Fallback if you haven't written the math yet


# 1. PUBLIC API (Search & Map)

@app.route('/api/hospitals', methods=['GET'])
def get_hospitals():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    
    # SECURITY: Only return verified hospitals to the public map
    hospitals = Hospital.query.filter_by(is_verified=True).all()
    
    if lat and lng:
        hospitals = sort_hospitals_by_proximity(lat, lng, hospitals)
        
    results = []
    for h in hospitals:
        resources = [{'id': res.id, 'type': res.resource_type, 'available': res.available, 'price': res.price} for res in h.resources]
        results.append({
            'id': h.id,
            'name': h.name,
            'address': h.address,
            'latitude': h.latitude,
            'longitude': h.longitude,
            'hosp_type': h.hosp_type,
            'distance': getattr(h, 'distance', None), # Will be populated if geo_utils is used
            'resources': resources,
            'last_updated': h.last_updated.isoformat() + 'Z'
        })
    return jsonify(results)


# 2. TOKEN HANDSHAKE ENGINE

@app.route('/api/request-token', methods=['POST'])
def create_token():
    data = request.json
    h_id = data.get('hospital_id')
    mobile = data.get('mobile')
    
    if not mobile or len(mobile) != 10:
        return jsonify({'error': 'Invalid mobile number'}), 400
    

    # NEW SECURITY SHIELD: Check if user is officially blocked
    is_banned = BlockedUser.query.filter_by(mobile=mobile, is_blocked=True).first()
    if is_banned:
        return jsonify({'error': 'This mobile number has been suspended by an Administrator.'}), 403
    


        
    token = f"TK-{str(uuid.uuid4())[:6].upper()}"
    
    # 1. Save Permanent Record to SQLite
    new_request = ResourceRequest(token=token, user_mobile=mobile, hospital_id=h_id, status='Pending')
    db.session.add(new_request)
    db.session.commit()
    
    # 2. Save Temporary "Soft-Lock" to Redis (Expires in 1800s / 30 mins)
    r.setex(f"token:{token}", 1800, h_id)
    
    return jsonify({'token': token, 'status': 'Pending'})

@app.route('/api/my-applications', methods=['GET'])
def get_applications():
    mobile = request.args.get('mobile')
    reqs = ResourceRequest.query.filter_by(user_mobile=mobile).all()
    return jsonify([{'token': req.token, 'hospital': req.hospital.name, 'status': req.status, 'timestamp': req.timestamp.isoformat() + 'Z'} for req in reqs])


# 3. HOSPITAL PORTAL API

@app.route('/api/hospital/<int:h_id>/dashboard', methods=['GET'])
def get_hospital_dashboard(h_id):
    hospital = Hospital.query.get(h_id)
    if not hospital:
        return jsonify({'error': 'Hospital not found'}), 404
        
    resources = [{'id': res.id, 'type': res.resource_type, 'available': res.available, 'price': res.price} for res in hospital.resources]
    
    # Fetch all requests for this specific hospital
    requests = [{'token': req.token, 'mobile': req.user_mobile, 'status': req.status, 'timestamp': req.timestamp.isoformat()+'Z'} for req in hospital.requests]
    
    return jsonify({
        'id': hospital.id,
        'name': hospital.name,
        'address': hospital.address,
        'resources': resources,
        'requests': requests
    })

@app.route('/api/hospitals/<int:h_id>/update', methods=['POST'])
def update_resource(h_id):
    data = request.json
    res_type = data.get('type')
    change = data.get('change') # Usually 1 or -1
    
    resource = Resource.query.filter_by(hospital_id=h_id, resource_type=res_type).first()
    if resource:
        # Prevent negative beds
        resource.available = max(0, resource.available + change)
        
        # Log the change for accountability
        log = AuditLog(action=f"Updated {res_type}", details=f"Hospital ID {h_id} changed by {change}")
        db.session.add(log)
        
        # Touch the hospital to update the `last_updated` timestamp automatically
        hospital = Hospital.query.get(h_id)
        hospital.is_verified = True 
        

        hospital.last_updated = datetime.utcnow()



        db.session.commit()
        return jsonify({'status': 'success', 'new_count': resource.available})
    
    return jsonify({'status': 'error', 'message': 'Resource not found'}), 404

@app.route('/api/hospital/token-decision', methods=['POST'])
def token_decision():
    data = request.json
    token_str = data.get('token')
    decision = data.get('decision') # 'Accepted' or 'Denied'
    
    # 1. Update SQLite Status
    req = ResourceRequest.query.filter_by(token=token_str).first()
    if req:
        req.status = decision
        db.session.commit()
    
    # 2. Remove from Redis to free up the system
    r.delete(f"token:{token_str}")
    
    return jsonify({'status': 'Success', 'new_status': decision})

# ==========================================
# 4. INITIALIZATION
# ==========================================
def seed_data():
    with app.app_context():
        db.create_all()
        # Only seed if the database is completely empty  hard coaded just for prototype will use password hashing in actual production
        if not Hospital.query.first():
            h1 = Hospital(username="paras", password="123", name="Paras HMRI", address="Raja Bazar", latitude=25.605, longitude=85.082, hosp_type="Private", is_verified=True)
            h2 = Hospital(username="pmch", password="123", name="Patna Medical College", address="Ashok Rajpath", latitude=25.618, longitude=85.1666, hosp_type="Government", is_verified=True)
            db.session.add_all([h1, h2])
            db.session.commit()
            
            db.session.add_all([
                Resource(hospital_id=h1.id, resource_type="ICU Bed", available=5, price=8000.0),
                Resource(hospital_id=h1.id, resource_type="General Bed", available=15, price=2000.0),
                Resource(hospital_id=h1.id, resource_type="Ventilator", available=2, price=3000.0),
                Resource(hospital_id=h2.id, resource_type="ICU Bed", available=1, price=0.0),
                Resource(hospital_id=h2.id, resource_type="General Bed", available=40, price=0.0)
            ])
            db.session.commit()












# 5. AUTHENTICATION & REGISTRATION

@app.route('/api/register-hospital', methods=['POST'])
def register_hospital():
    data = request.json
    
    # Check if username exists
    if Hospital.query.filter_by(username=data.get('username')).first():
        return jsonify({'error': 'Username already taken'}), 400
        
    new_hosp = Hospital(
        username=data.get('username'),
        password=data.get('password'), # In production, i must hash this!
        name=data.get('name'),
        address=data.get('address'),
        latitude=float(data.get('latitude')),
        longitude=float(data.get('longitude')),
        hosp_type=data.get('hosp_type'),
        description=data.get('description', ''),
        is_verified=False # Admin MUST verify this later
    )
    db.session.add(new_hosp)
    db.session.commit()
    
    # Initialize basic resources at 0 so the dashboard doesn't crash
    db.session.add_all([
        Resource(hospital_id=new_hosp.id, resource_type="ICU Bed", available=0, price=0.0),
        Resource(hospital_id=new_hosp.id, resource_type="General Bed", available=0, price=0.0),
        Resource(hospital_id=new_hosp.id, resource_type="Ventilator", available=0, price=0.0)
    ])
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Registration submitted for admin approval.'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # # 1. Check Admin Hardcode
    # if username == 'admin' and password == '123':
    #     return jsonify({'role': 'admin', 'token': 'admin-token-123'})



    # 1. Secure Admin Check using Environment Variables
    admin_user = os.getenv('ADMIN_USERNAME', 'admin')
    admin_pass = os.getenv('ADMIN_PASSWORD', 'secure_fallback_123') 
    
    if username == admin_user and password == admin_pass:
        return jsonify({'role': 'admin', 'token': 'admin-token-123'})






        
    # 2. Check Hospital Database
    hospital = Hospital.query.filter_by(username=username, password=password).first()
    # In a real app, we will use werkzeug.security to check a hashed password here.
    # For this hackathon prototype, we check the direct stringfrom database.
    if hospital:
        if not hospital.is_verified:
            return jsonify({'error': 'Account pending admin verification.'}), 403
        return jsonify({
            'role': 'hospital',
            'hospital_id': hospital.id,
            'name': hospital.name,
            'token': f'hosp-token-{hospital.id}'
        })
        
    return jsonify({'error': 'Invalid credentials'}), 401


# 6. ADMIN DASHBOARD API

@app.route('/api/admin/unverified', methods=['GET'])
def get_unverified():
    # Only fetch hospitals waiting for approval
    hospitals = Hospital.query.filter_by(is_verified=False).all()
    results = [{'id': h.id, 'name': h.name, 'address': h.address, 'type': h.hosp_type, 'date': h.last_updated.isoformat() + 'Z'} for h in hospitals]
    return jsonify(results)

@app.route('/api/admin/verify/<int:h_id>', methods=['POST'])
def verify_hospital(h_id):
    hospital = Hospital.query.get(h_id)
    if hospital:
        hospital.is_verified = True
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Not found'}), 404



























# --- NEW HOSPITAL ACTIONS ---
@app.route('/api/hospital/<int:h_id>/add-resource', methods=['POST'])
def add_custom_resource(h_id):
    data = request.json
    res_type = data.get('type')
    
    # Prevent duplicate resource types for the same hospital
    if Resource.query.filter_by(hospital_id=h_id, resource_type=res_type).first():
        return jsonify({'error': 'Resource type already exists.'}), 400
        
    new_res = Resource(
        hospital_id=h_id,
        resource_type=res_type,
        available=int(data.get('available', 0)),
        price=float(data.get('price', 0.0))
    )
    db.session.add(new_res)







    # THE FIX: Explicitly update the hospital's timestamp
    hospital = Hospital.query.get(h_id)
    hospital.last_updated = datetime.utcnow()




    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/hospital/report-user', methods=['POST'])
def report_user():
    data = request.json
    mobile = data.get('mobile')
    h_id = data.get('hospital_id')
    
    # Check if already reported
    if BlockedUser.query.filter_by(mobile=mobile).first():
        return jsonify({'error': 'User already reported.'}), 400
        
    report = BlockedUser(mobile=mobile, reason="Spam / Fake Request", reported_by=h_id)
    db.session.add(report)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'User reported to Admin.'})













@app.route('/api/hospital/<int:h_id>/resource/<string:res_type>', methods=['DELETE'])
def delete_resource(h_id, res_type):
    # Find the specific resource for this specific hospital
    resource = Resource.query.filter_by(hospital_id=h_id, resource_type=res_type).first()
    
    if resource:
        db.session.delete(resource)
        
        # Log the deletion
        log = AuditLog(action=f"Deleted {res_type}", details=f"Hospital ID {h_id} permanently removed resource tracking.")
        db.session.add(log)
        
        # Touch the hospital timestamp so the public map knows it was updated
        hospital = Hospital.query.get(h_id)
        hospital.last_updated = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'status': 'success'})
        
    return jsonify({'error': 'Resource not found'}), 404












# --- NEW ADMIN ACTIONS ---
@app.route('/api/admin/reports', methods=['GET'])
def get_reports():
    reports = BlockedUser.query.filter_by(is_blocked=False).all()
    results = [{'id': r.id, 'mobile': r.mobile, 'reason': r.reason, 'date': r.timestamp.isoformat() + 'Z'} for r in reports]
    return jsonify(results)

@app.route('/api/admin/block-user/<int:report_id>', methods=['POST'])
def block_user(report_id):
    report = BlockedUser.query.get(report_id)
    if report:
        report.is_blocked = True
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Report not found'}), 404







@app.route('/api/cancel-request', methods=['POST'])
def cancel_request():
    data = request.json
    token_str = data.get('token')
    
    req = ResourceRequest.query.filter_by(token=token_str).first()
    
    if not req:
        return jsonify({'error': 'Token not found.'}), 404
        
    if req.status != 'Pending':
        return jsonify({'error': 'Cannot cancel a request that has already been Accepted or Denied.'}), 400
        
    # Update SQLite History
    req.status = 'Cancelled'
    db.session.commit()
    
    # FREE THE BED: Remove from Redis so the hospital dashboard drops it
    r.delete(f"token:{token_str}")
    
    return jsonify({'status': 'Success', 'message': 'Request cancelled successfully.'})



if __name__ == '__main__':
    #seed_data()
    # app.run( port=5000)


    @app.route('/api/admin/force-build-db', methods=['GET'])
    def force_build_db():
        try:
            # This forces the app to create the tables and inject the hospital data
            db.create_all()
            seed_data()
            return jsonify({'status': 'success', 'message': 'Production database built and seeded successfully!'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    CORS(app)