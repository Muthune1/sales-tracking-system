# Sales Force Tracking System - Complete Architecture

## System Overview

A real-time sales personnel tracking system with mobile app, backend API, and manager dashboard for monitoring field sales activity with location validation.

---

## Production Tech Stack

### 1. Mobile Application (Field Personnel)

**Framework:** React Native or Flutter
- Cross-platform iOS and Android support
- Native GPS access and camera integration
- Offline-first architecture with background sync

**Key Features:**
```javascript
// Core functionality
- Auto check-in/check-out with geofencing (50m radius)
- Background location tracking
- Selfie capture with EXIF metadata (GPS, timestamp)
- Offline data storage with SQLite
- Auto-sync when network available
- Push notifications for reminders
- Daily route planning
```

**Tech Components:**
```
React Native:
- react-native-maps
- react-native-geolocation-service
- react-native-camera
- @react-native-async-storage/async-storage
- react-native-background-fetch

Flutter:
- geolocator
- google_maps_flutter
- camera
- sqflite
- connectivity_plus
```

---

### 2. Backend API

**Primary Stack:** FastAPI (Python) or Node.js/Express

**Database:**
```sql
PostgreSQL with PostGIS extension

-- Tables
CREATE TABLE personnel (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    employee_id VARCHAR(50) UNIQUE,
    manager_id INTEGER REFERENCES personnel(id),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    address TEXT,
    coordinates GEOGRAPHY(POINT, 4326),
    geofence_radius INTEGER DEFAULT 50, -- meters
    location_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE visits (
    id SERIAL PRIMARY KEY,
    personnel_id INTEGER REFERENCES personnel(id),
    location_id INTEGER REFERENCES locations(id),
    planned_date DATE,
    check_in_time TIMESTAMP,
    check_in_coords GEOGRAPHY(POINT, 4326),
    check_out_time TIMESTAMP,
    check_out_coords GEOGRAPHY(POINT, 4326),
    duration_minutes INTEGER,
    selfie_url TEXT,
    selfie_metadata JSONB,
    notes TEXT,
    validated BOOLEAN DEFAULT false,
    validation_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE daily_sessions (
    id SERIAL PRIMARY KEY,
    personnel_id INTEGER REFERENCES personnel(id),
    session_date DATE,
    login_time TIMESTAMP,
    logout_time TIMESTAMP,
    total_visits INTEGER,
    total_travel_km DECIMAL(10,2),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE location_validations (
    id SERIAL PRIMARY KEY,
    visit_id INTEGER REFERENCES visits(id),
    validation_type VARCHAR(50), -- GPS, Photo, Manual
    is_valid BOOLEAN,
    distance_from_location DECIMAL(10,2), -- meters
    validation_details JSONB,
    validated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_visits_personnel_date ON visits(personnel_id, planned_date);
CREATE INDEX idx_visits_location ON visits(location_id);
CREATE INDEX idx_visits_check_in ON visits(check_in_time);
CREATE SPATIAL INDEX idx_location_coords ON locations USING GIST(coordinates);
```

**API Endpoints:**
```python
# FastAPI example structure

from fastapi import FastAPI, WebSocket, Depends
from sqlalchemy.orm import Session
import redis.asyncio as redis

app = FastAPI()

# Authentication
@app.post("/api/v1/auth/login")
async def login(credentials: LoginModel):
    """Mobile app login"""
    pass

# Check-in/out
@app.post("/api/v1/visits/check-in")
async def check_in(visit_data: CheckInModel, db: Session):
    """
    Validate location and create check-in
    - Verify GPS coordinates within geofence
    - Store selfie with metadata
    - Update real-time dashboard via WebSocket
    """
    pass

@app.post("/api/v1/visits/check-out")
async def check_out(visit_id: int, checkout_data: CheckOutModel):
    """Record check-out with location validation"""
    pass

# Location management
@app.get("/api/v1/locations/nearby")
async def get_nearby_locations(lat: float, lon: float, radius: int = 5000):
    """Get locations within radius for route planning"""
    pass

@app.post("/api/v1/locations/validate")
async def validate_location(coords: CoordinatesModel, location_id: int):
    """
    Validate if coordinates are within geofence
    Returns: {valid: bool, distance: float}
    """
    pass

# Dashboard APIs
@app.get("/api/v1/dashboard/team-summary")
async def get_team_summary(manager_id: int, date_range: DateRange):
    """Team-wide KPIs and metrics"""
    pass

@app.get("/api/v1/dashboard/personnel/{personnel_id}")
async def get_personnel_details(personnel_id: int, date_range: DateRange):
    """Individual performance data"""
    pass

# Real-time updates
@app.websocket("/ws/dashboard/{manager_id}")
async def websocket_endpoint(websocket: WebSocket, manager_id: int):
    """
    Real-time dashboard updates
    Sends: check-ins, check-outs, location updates
    """
    await websocket.accept()
    while True:
        # Listen to Redis pub/sub for updates
        data = await redis_client.subscribe(f"team:{manager_id}")
        await websocket.send_json(data)

# Background jobs (Celery)
@celery.task
def validate_visit_locations():
    """Batch validate visits using Google Maps API"""
    pass

@celery.task
def generate_daily_reports():
    """Generate end-of-day reports for managers"""
    pass

@celery.task
def send_reminder_notifications():
    """Send push notifications for pending check-ins"""
    pass
```

**Caching Strategy (Redis):**
```python
# Cache frequently accessed data
redis_client = redis.from_url("redis://localhost:6379")

# Cache team metrics (5 min TTL)
await redis_client.setex(
    f"team:metrics:{manager_id}:{date}",
    300,
    json.dumps(metrics)
)

# Real-time updates pub/sub
await redis_client.publish(
    f"team:{manager_id}",
    json.dumps({"type": "check_in", "data": visit_data})
)
```

---

### 3. Manager Dashboard (Web)

**Framework:** React with TypeScript

**Real-time Updates:**
```javascript
// WebSocket connection
import { io } from 'socket.io-client';

const socket = io('wss://api.example.com');

socket.on('visit_update', (data) => {
  // Update dashboard in real-time
  updateVisitMarker(data);
  refreshMetrics();
});

socket.on('team_alert', (alert) => {
  showNotification(alert);
});
```

**Map Integration:**
```javascript
// Mapbox GL JS for location visualization
import mapboxgl from 'mapbox-gl';

// Show real-time personnel locations
const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/streets-v11',
  center: [77.5946, 12.9716], // Bengaluru
  zoom: 11
});

// Add markers for each salesperson
personnel.forEach(person => {
  new mapboxgl.Marker({ color: person.status === 'active' ? 'green' : 'gray' })
    .setLngLat([person.lon, person.lat])
    .setPopup(new mapboxgl.Popup().setHTML(`<h3>${person.name}</h3>`))
    .addTo(map);
});

// Draw geofences
locations.forEach(loc => {
  map.addLayer({
    id: `geofence-${loc.id}`,
    type: 'circle',
    source: {
      type: 'geojson',
      data: {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [loc.lon, loc.lat]
        }
      }
    },
    paint: {
      'circle-radius': loc.geofence_radius,
      'circle-color': '#4264fb',
      'circle-opacity': 0.2
    }
  });
});
```

**Dashboard Components:**
```typescript
// Key dashboard views
interface DashboardViews {
  TeamOverview: {
    liveMap: MapComponent;
    kpis: MetricsPanel;
    teamActivity: ActivityFeed;
    alerts: AlertsPanel;
  };
  
  IndividualView: {
    personnelSelector: Dropdown;
    visitHistory: Timeline;
    performanceMetrics: ChartPanel;
    locationMap: MapComponent;
  };
  
  Analytics: {
    trendCharts: Charts;
    heatmaps: HeatmapView;
    comparisons: ComparisonPanel;
  };
  
  Reports: {
    dailyReport: ReportGenerator;
    weeklyReport: ReportGenerator;
    exportOptions: ExportPanel;
  };
}
```

---

### 4. Location Validation System

**Geofencing Validation:**
```python
from geopy.distance import geodesic

def validate_check_in(visit_coords, location_coords, geofence_radius=50):
    """
    Validate if check-in coordinates are within geofence
    
    Args:
        visit_coords: (lat, lon) tuple from mobile app
        location_coords: (lat, lon) tuple from database
        geofence_radius: radius in meters
    
    Returns:
        {
            'valid': bool,
            'distance': float,  # meters
            'status': str
        }
    """
    distance = geodesic(visit_coords, location_coords).meters
    
    if distance <= geofence_radius:
        status = 'VALID'
        valid = True
    elif distance <= geofence_radius * 2:
        status = 'WARNING'  # Near but not exact
        valid = True
    else:
        status = 'INVALID'
        valid = False
    
    return {
        'valid': valid,
        'distance': round(distance, 2),
        'status': status
    }
```

**Photo Validation:**
```python
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def validate_selfie_metadata(image_path):
    """
    Extract and validate GPS data from photo EXIF
    """
    image = Image.open(image_path)
    exif_data = image._getexif()
    
    gps_info = {}
    for tag, value in exif_data.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            for gps_tag in value:
                sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                gps_info[sub_decoded] = value[gps_tag]
    
    # Extract lat/lon
    lat = convert_to_degrees(gps_info['GPSLatitude'])
    lon = convert_to_degrees(gps_info['GPSLongitude'])
    timestamp = gps_info.get('GPSTimeStamp')
    
    return {
        'coordinates': (lat, lon),
        'timestamp': timestamp,
        'camera_make': exif_data.get('Make'),
        'camera_model': exif_data.get('Model')
    }
```

---

### 5. Infrastructure & DevOps

**Cloud Architecture (AWS Example):**
```
┌─────────────────────────────────────────────────────┐
│                   Route 53 (DNS)                    │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│           CloudFront (CDN)                          │
│           - Dashboard static files                   │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│        Application Load Balancer                    │
└─────────┬────────────────────────────┬──────────────┘
          │                            │
┌─────────▼─────────┐      ┌──────────▼──────────────┐
│  ECS/Fargate      │      │   Lambda Functions      │
│  - API Servers    │      │   - Image processing    │
│  - WebSocket      │      │   - Report generation   │
└─────────┬─────────┘      └─────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────┐
│              Amazon RDS (PostgreSQL)                │
│              - Multi-AZ                             │
│              - Read replicas                        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│         Amazon ElastiCache (Redis)                  │
│         - Session management                        │
│         - Real-time cache                           │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              S3 Buckets                             │
│              - Selfie images                        │
│              - Generated reports                    │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│         Amazon SNS/SQS                              │
│         - Push notifications                        │
│         - Background job queue                      │
└─────────────────────────────────────────────────────┘
```

**Docker Compose (Development):**
```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/salesdb
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis

  dashboard:
    build: ./dashboard
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000

  db:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: salesdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery_worker:
    build: ./backend
    command: celery -A app.celery worker --loglevel=info
    depends_on:
      - redis
      - db

  celery_beat:
    build: ./backend
    command: celery -A app.celery beat --loglevel=info
    depends_on:
      - redis

volumes:
  postgres_data:
```

---

## Data Flow

```
Mobile App (Field Personnel)
    ↓ GPS + Selfie + Timestamp
API Gateway
    ↓ Validate Location
PostgreSQL (Store Visit)
    ↓ Publish Event
Redis Pub/Sub
    ↓ Real-time Update
WebSocket
    ↓ Push to Client
Dashboard (Manager View)
    ↓ Visual Update
```

---

## Security Measures

1. **Authentication:**
   - JWT tokens with refresh mechanism
   - OAuth 2.0 for social login
   - Multi-factor authentication for managers

2. **Data Security:**
   - TLS/SSL for all communications
   - Encrypted storage for sensitive data
   - Photo storage with pre-signed URLs (time-limited access)

3. **Privacy:**
   - Location tracking only during work hours
   - GDPR compliance for data retention
   - User consent for tracking

4. **API Security:**
   - Rate limiting (100 req/min per user)
   - API key authentication for external integrations
   - Input validation and sanitization

---

## Monitoring & Analytics

**Application Monitoring:**
- Sentry for error tracking
- New Relic/DataDog for performance
- CloudWatch for infrastructure metrics

**Business Analytics:**
- Track visit completion rates
- Average time per location
- Route optimization suggestions
- Performance comparisons

**Alerts:**
- Late check-ins
- Missing check-outs
- GPS validation failures
- System health issues

---

## Mobile App Schema

```javascript
// AsyncStorage schema for offline mode

const schemas = {
  visits: {
    id: 'local_id',
    server_id: null,  // Null until synced
    location_id: 123,
    check_in_time: '2024-02-14T09:30:00',
    check_in_coords: { lat: 12.9716, lon: 77.5946 },
    check_out_time: null,
    check_out_coords: null,
    selfie_path: 'file://local/path/selfie.jpg',
    notes: '',
    synced: false,
    sync_attempts: 0,
    created_at: '2024-02-14T09:30:00'
  },
  
  pending_uploads: {
    type: 'selfie',
    local_path: 'file://path',
    visit_id: 'local_123',
    retry_count: 0,
    last_attempt: null
  }
}

// Sync logic
async function syncPendingData() {
  const pending = await AsyncStorage.getItem('pending_visits');
  
  for (const visit of pending) {
    try {
      // Upload selfie first
      const selfieUrl = await uploadSelfie(visit.selfie_path);
      
      // Create visit record
      const response = await api.post('/visits/check-in', {
        ...visit,
        selfie_url: selfieUrl
      });
      
      // Mark as synced
      visit.synced = true;
      visit.server_id = response.data.id;
      
    } catch (error) {
      visit.sync_attempts++;
      // Retry later
    }
  }
}
```

---

## Cost Estimation (AWS)

**Monthly costs for 100 sales personnel:**

- EC2/ECS: $200/month (t3.medium instances)
- RDS PostgreSQL: $150/month (db.t3.small Multi-AZ)
- ElastiCache: $50/month (cache.t3.micro)
- S3: $20/month (image storage)
- CloudFront: $30/month (CDN)
- Data Transfer: $50/month
- **Total: ~$500/month**

For 1000 personnel: ~$2000-3000/month

---

## Implementation Timeline

**Phase 1 (Month 1-2):** MVP
- Basic mobile app (check-in/out)
- Simple dashboard
- PostgreSQL setup
- Basic location validation

**Phase 2 (Month 3-4):** Enhanced Features
- Offline mode
- Photo validation
- Real-time updates
- Advanced analytics

**Phase 3 (Month 5-6):** Production Ready
- Performance optimization
- Security hardening
- Load testing
- Production deployment

**Phase 4 (Month 6+):** Advanced Features
- AI-powered route optimization
- Predictive analytics
- Advanced reporting
- Mobile app improvements
