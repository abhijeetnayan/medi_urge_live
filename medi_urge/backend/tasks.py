from celery import Celery
from datetime import datetime, timedelta
import os

def make_celery(app_name):
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    return Celery(app_name, broker=redis_url, backend=redis_url)

celery = make_celery('medical_tracker')

@celery.task
def check_stale_data():
    """
    Task to check for hospitals that haven't updated their data in 6 hours
    and mark them as unverified.
    """
    from app import app, db, Hospital
    with app.app_context():
        six_hours_ago = datetime.utcnow() - timedelta(hours=6)
        stale_hospitals = Hospital.query.filter(Hospital.last_updated < six_hours_ago).all()
        
        for hospital in stale_hospitals:
            hospital.is_verified = False
        
        db.session.commit()
        return f"Processed {len(stale_hospitals)} stale records."
