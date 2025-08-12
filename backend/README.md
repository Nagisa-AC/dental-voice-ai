# Dental Voice AI - Production Backend

A production-ready FastAPI backend for dental practice voice AI integration with VAPI.

## 🏗️ Architecture

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core utilities and configurations
│   │   ├── config.py           # Application configuration
│   │   ├── database.py         # Database operations
│   │   └── schemas.py          # Pydantic data models
│   ├── intelligence/           # AI processing and intent recognition
│   │   └── dental_faq_matcher.py
│   └── api/                    # API endpoints
│       └── v1/                 # API version 1
│           └── dental.py       # Dental Voice AI endpoints
├── requirements.txt            # Python dependencies
└── docs/                       # Documentation
    ├── schemas/               # Database schemas
    └── prompts/               # AI prompts & VAPI configs
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Supabase account
- ngrok (for local development)

### Installation
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration
Set environment variables:
```bash
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_anon_key"
export ENVIRONMENT="development"
```

### Run Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Expose with ngrok
```bash
ngrok http 8000
```

## 📋 API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /health` - Detailed system health
- `GET /config` - Configuration info (dev only)

### Dental Voice AI Endpoints (v1)
- `GET /dental/availability` - Get appointment slots
- `POST /dental/appointment_store` - Store appointments (VAPI)
- `POST /dental/incoming_call` - VAPI webhook handler
- `GET /dental/incoming_call` - VAPI availability check
- `POST /dental/analyze_intent` - Intent analysis

## 🔧 VAPI Integration

### Required Tools
1. **`get_tenant_appointment_availability`** (GET)
   - URL: `/dental/availability?tenant_id=UUID`
   - Returns: Available appointment slots

2. **`post_tenant_apointment`** (POST)
   - URL: `/dental/appointment_store`
   - Stores: Appointment data in `appointment_requests` table

### VAPI Configuration
```json
{
  "name": "get_tenant_appointment_availability",
  "url": "https://your-domain.com/dental/availability",
  "method": "GET",
  "variableExtractionPlan": {
    "schema": {
      "type": "object",
      "required": ["message", "success", "available_slots"],
      "properties": {
        "message": {"type": "string"},
        "success": {"type": "boolean"},
        "available_slots": {"type": "string"}
      }
    }
  }
}
```

## 🗄️ Database Schema

### Core Tables
- `tenants` - Dental practice information
- `calls` - Call transcripts and analysis
- `appointment_requests` - Appointment bookings
- `office_availabilities` - Available time slots

### Key Relationships
- All tables reference `tenants.id` for multi-practice support
- `appointment_requests` stores confirmed appointments
- `office_availabilities` manages available time slots

## 🧪 Testing

### Manual Testing
```bash
# Test availability endpoint
curl "http://localhost:8000/dental/availability?tenant_id=your-tenant-id"

# Test appointment storage
curl -X POST "http://localhost:8000/dental/appointment_store" \
  -H "Content-Type: application/json" \
  -d '{
    "function": {
      "arguments": "{\"patient_name\":\"John Doe\",\"phone_number\":\"1234567890\",\"appointment_date\":\"2025-08-15\",\"appointment_time\":\"14:30\",\"reason\":\"Cleaning\"}"
    }
  }'
```

## 📚 Documentation

- **Database Schemas**: `docs/schemas/` - Complete database schema and documentation
- **AI Prompts**: `docs/prompts/` - VAPI configurations and assistant prompts
- **API Reference**: See endpoints section above

## 🔍 Monitoring

### Health Checks
- Database connectivity
- Supabase client status
- Endpoint availability

### Logging
- Structured logging with request IDs
- Error tracking and debugging
- Performance monitoring

## 🚀 Production Deployment

### Environment Variables
```bash
ENVIRONMENT=production
SUPABASE_URL=your_production_url
SUPABASE_KEY=your_production_key
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-domain.com
```

### Security
- CORS configuration for production domains
- Environment-based configuration
- Secure database connections

## 📈 Performance

### Optimizations
- Efficient database queries with indexes
- Async/await for I/O operations
- Structured error handling
- Minimal memory footprint

### Scalability
- Stateless design
- Database connection pooling
- Horizontal scaling ready

## 🔧 Development

### Code Style
- Type hints throughout
- Comprehensive docstrings
- Consistent naming conventions
- Error handling patterns

### Architecture Principles
- Single responsibility
- Dependency injection
- Clean separation of concerns
- Minimal coupling

## 📝 Changelog

### v1.0.0 (Current)
- ✅ VAPI integration complete
- ✅ Appointment booking system
- ✅ Intent recognition
- ✅ Multi-practice support
- ✅ Production-ready error handling
- ✅ Clean architecture reorganization

## 🤝 Contributing

1. Follow existing code patterns
2. Add type hints and docstrings
3. Include error handling
4. Test thoroughly
5. Update documentation

## 📄 License

Proprietary - All rights reserved