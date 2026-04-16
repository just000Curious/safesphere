# SafeSphere - Emergency Response Platform

A comprehensive safety and emergency management system with real-time alerts, location tracking, and incident management.

## 📋 Project Overview

SafeSphere is an integrated platform designed to help manage safety incidents and emergency situations. It includes:

- **User Management** - User registration, authentication, and profile management
- **Real-time Alerts** - Create and manage emergency alerts with escalation
- **Location Tracking** - Track user locations on maps using geolocation
- **Incident Management** - Log, track, and manage incidents
- **Dashboards** - Admin and user dashboards for monitoring and analytics
- **Real-time Notifications** - WebSocket-based instant notifications
- **Mobile Support** - Web-based interface accessible from any device

## 🏗️ Project Structure

```
SafeSphere/
├── backend/          # Python FastAPI server
│   ├── app/
│   │   ├── api/      # API endpoints (auth, users, alerts, etc.)
│   │   ├── models/   # Database models
│   │   ├── schemas/  # Data validation schemas
│   │   ├── services/ # Business logic (notifications, escalation, ML)
│   │   └── core/     # Database, security, dependencies
│   └── alembic/      # Database migrations
├── frontend/         # React + Vite web application
│   └── src/
│       ├── components/    # Reusable UI components
│       ├── pages/         # Page components
│       ├── context/       # React context (auth, toast)
│       └── api.js         # API communication
└── streamlit_app/    # Streamlit dashboard for analytics
    ├── app.py
    └── pages/        # Dashboard pages
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** (for backend and streamlit app)
- **Node.js 16+** (for frontend)
- **PostgreSQL** (for database)
- **Redis** (for caching and background tasks)
- **Git** (for version control)

### 1️⃣ Backend Setup

#### Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Step 2: Set Up Environment Variables

Create a `.env` file in the `backend` directory:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/safesphere
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
GOOGLE_MAPS_API_KEY=your-google-maps-key
```

#### Step 3: Initialize Database

```bash
cd backend
alembic upgrade head
```

#### Step 4: Run the Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

---

### 2️⃣ Frontend Setup

#### Step 1: Install Node Dependencies

```bash
cd frontend
npm install
```

#### Step 2: Start Development Server

```bash
npm run dev
```

The frontend will be available at: `http://localhost:5173`

#### Step 3: Build for Production

```bash
npm run build
```

---

### 3️⃣ Streamlit Dashboard Setup (Optional)

#### Step 1: Install Dependencies

```bash
cd streamlit_app
pip install streamlit
```

#### Step 2: Run Streamlit App

```bash
streamlit run app.py
```

The dashboard will be available at: `http://localhost:8501`

---

## 📚 How to Use

### Register a New User

1. Go to `http://localhost:5173`
2. Click "Register"
3. Enter email, password, and personal details
4. Submit the form

### Create an Alert

1. Log in to your account
2. Navigate to the Alerts section
3. Click "Create Alert"
4. Fill in alert details and trigger type
5. Alert will be sent to designated contacts

### View Location Map

1. Go to Dashboard
2. View real-time user locations on the map
3. Click on markers to see user details

### Access Admin Dashboard

1. Log in as admin
2. View system statistics and analytics
3. Manage incidents and user accounts

---

## 🔧 Development Commands

### Backend

```bash
# Run tests
python -m pytest

# Create database migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Frontend

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint

# Preview production build
npm run preview
```

---

## 🛑 Stopping Services

### Stop Backend
```bash
# Press Ctrl+C in the terminal running the backend
```

### Stop Frontend
```bash
# Press Ctrl+C in the terminal running the frontend
```

### Stop Streamlit
```bash
# Press Ctrl+C in the terminal running streamlit
```

---

## 📝 Database Setup

### Create PostgreSQL Database

```sql
CREATE DATABASE safesphere;
```

### Create Redis Connection

Make sure Redis is running:

```bash
# Windows (if installed)
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis
```

---

## 🐳 Docker Setup (Alternative)

If you prefer using Docker, you can run the entire stack:

```bash
docker-compose up
```

(Requires `docker-compose.yml` to be set up)

---

## 🔐 Security Notes

- **Never commit `.env` files** - Keep credentials private
- **Change `SECRET_KEY`** in production
- **Use HTTPS** in production (not HTTP)
- **Set `allow_origins`** to specific domains in production (not `*`)
- **Database credentials** should be strong and unique

---

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify PostgreSQL is running
- Check `.env` file configuration

### Frontend won't load
- Check if port 5173 is available
- Clear browser cache and restart
- Ensure backend is running

### Database connection errors
- Verify PostgreSQL credentials in `.env`
- Check if PostgreSQL service is running
- Ensure database `safesphere` exists

### WebSocket connection issues
- Verify backend is running
- Check browser console for errors
- Ensure CORS settings are correct

---

## 📞 Support

For issues or questions:
1. Check this README
2. Review API documentation at `/docs`
3. Check application logs in backend

---

## 📄 License

[Add your license here]

---

## 👥 Contributors

[Add contributors here]

---

**Happy coding! 🎉**
