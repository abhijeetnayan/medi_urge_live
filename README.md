# Intra-City Medical Resource Tracker

A high-performance medical resource tracking system built with Vue.js 3 and Flask. It allows emergency services to track ICU beds, ventilators, and oxygen in real-time with proximity sorting and geospatial visualization.

## Features

- **Split-Screen Map Search**: Search for hospitals using Leaflet.js maps.
- **Real-time Proximity Engine**: Hospitals are sorted based on user location (browser Geolocation).
- **Admin Dashboard**: Secure management console for hospital staff to update counts.
- **Resource Booking**: Redis-backed token system for 30-minute "bed-racing" prevention.
- **Verification Engine**: Background worker (Celery) flags stale data if not updated within 6 hours.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Redis (for tokens and background tasks)



# MediUrge - Real-Time Hospital Resource Tracker

A full-stack application built for Byte hack that connects patients to real-time hospital bed availability and prevents bed-hoarding using a Redis-backed token handshake system.

## Tech Stack
* **Frontend:** Vue 3, Pinia, Bootstrap 5, Leaflet.js
* **Backend:** Python, Flask, SQLite, Redis

## How to Run Locally

## Installation & Setup

### 1. Backend Setup
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python app.py

### 2. Frontend Setup
    cd frontend
    npm install
    npm run dev

### 3. Background Worker (Optional for Dev)
    # Ensure Redis is running locally
    cd backend
    celery -A tasks.celery worker --loglevel=info

## Project Structure

- `backend/`: Flask REST API, SQLAlchemy models, and Geolocation logic.
- `frontend/`: Vue 3 application using Vite and Pinia for state management.
- `geo_utils.py`: Contains the Haversine formula for distance calculation.
- `tasks.py`: Celery tasks for system maintenance and data integrity.

## Usage

1. Open the frontend at `http://localhost:5173`.
2. Browse the map to see hospital markers (Red for critical, Blue for available).
3. Use the "Admin Dashboard" to simulate updating hospital inventory.
4. Click "Request Resource" to generate a temporary tracking token.

## Troubleshooting

- **Redis Error**: Ensure Redis is running on port 6379 for the token system to work.
- **Map Not Loading**: Ensure you have an internet connection to fetch Leaflet tile layers.
- **API Connection**: The frontend uses a Vite proxy. Ensure the Flask app is running on port 5000.
