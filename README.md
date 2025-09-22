# 🏥 Dental Voice AI - Healthcare Practice Management System

A modern, AI-powered healthcare practice management system with VAPI voice integration, built with FastAPI and React.

## 🏗️ **New Project Structure**

```
dental-voice-ai/
├── backend/                    # 🐍 Python FastAPI Backend
│   ├── main.py                # Application entry point
│   ├── api/                   # FastAPI routes
│   │   └── v1/               # API version 1
│   │       ├── auth.py       # Authentication endpoints
│   │       ├── clinic.py     # Clinic management
│   │       ├── webhooks.py   # VAPI webhook handling ⭐
│   │       └── ...
│   ├── core/                 # Core configuration & utilities
│   │   ├── config.py         # Application configuration
│   │   ├── database.py       # Database connection management
│   │   ├── auth.py           # Authentication logic
│   │   └── logging_config.py # Logging setup
│   ├── db/                   # Database layer
│   │   ├── models/           # SQLAlchemy ORM models
│   │   │   ├── database_models.py  # All database models
│   │   │   └── pydantic_schemas.py # Pydantic schemas
│   │   └── migrations/       # Alembic migrations
│   ├── services/             # Business logic services
│   │   ├── auth_service.py   # Authentication service
│   │   ├── office_service.py # Clinic management
│   │   └── ...
│   ├── integrations/         # External service integrations
│   │   ├── vapi/            # VAPI voice AI integration
│   │   ├── supabase/        # Supabase database
│   │   └── google/          # Google Calendar API
│   ├── middleware/           # HTTP middleware
│   │   ├── audit_middleware.py
│   │   ├── csrf_middleware.py
│   │   └── rate_limiting_middleware.py
│   └── utils/               # Shared utilities
│
├── frontend/                 # ⚛️ React TypeScript Frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   │   ├── DesignSystem/ # Design system components
│   │   │   └── ErrorBoundary.tsx
│   │   ├── features/        # Feature modules
│   │   │   ├── auth/        # Authentication
│   │   │   ├── dashboard/   # Dashboard
│   │   │   └── landing/     # Landing page
│   │   ├── hooks/           # Custom React hooks
│   │   ├── layouts/         # Layout components
│   │   ├── contexts/        # React contexts
│   │   ├── types/           # TypeScript types
│   │   ├── utils/           # Utility functions
│   │   └── styles/          # Global styles
│   └── public/              # Static assets
│
├── tests/                   # 🧪 Test Suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/               # End-to-end tests
│
├── docs/                   # 📚 Documentation
│   ├── README.md          # Main documentation
│   ├── DEPLOYMENT.md      # Deployment guide
│   ├── SECURITY_SETUP.md  # Security configuration
│   └── legacy/            # Legacy documentation
│
├── infra/                  # 🏗️ Infrastructure & DevOps
│   ├── monitoring/        # Monitoring setup (Grafana, Prometheus)
│   ├── nginx/            # Nginx configuration
│   ├── docker/           # Docker configurations
│   └── prompts/          # AI prompts for VAPI
│
├── scripts/               # 🛠️ Utility Scripts
│   ├── reset_database.py  # Database management
│   ├── generate_schema.py # Schema generation
│   └── ...
│
└── config files           # ⚙️ Configuration
    ├── pyproject.toml     # Python project config
    ├── docker-compose.yml # Docker services
    ├── Dockerfile         # Container definition
    ├── Makefile          # Development commands
    └── alembic.ini       # Database migrations
```

## 🚀 **Quick Start**

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- Supabase account
- VAPI account

### Installation

```bash
# Clone the repository
git clone https://github.com/dental-voice-ai/dental-voice-ai.git
cd dental-voice-ai

# Run the setup script
chmod +x setup.sh
./setup.sh

# Start development environment
make dev
```

### Manual Setup

```bash
# Install Python dependencies
pip install -e ".[dev]"

# Install frontend dependencies
cd frontend && npm install && cd ..

# Copy environment template
cp .env.example .env
# Edit .env with your configuration

# Start development server
make dev-local
```

## 🔧 **Development Commands**

```bash
# Development
make dev              # Start with Docker
make dev-local        # Start locally
make dev-logs         # View logs
make dev-stop         # Stop services

# Testing
make test             # Run all tests
make test-unit        # Unit tests only
make test-integration # Integration tests
make test-e2e         # End-to-end tests

# Database
make db-migrate       # Run migrations
make db-reset         # Reset database
make db-status        # Check database status

# Code Quality
make lint             # Run linters
make format           # Format code
make type-check       # Type checking
```

## 🎯 **Key Features**

- **🔐 Security & Authentication**: JWT auth, CSRF protection, HTTPS enforcement
- **🏥 Healthcare Business Logic**: Clinic management, AI assistant integration
- **📞 VAPI Voice Integration**: AI-powered phone calls with appointment booking
- **📊 Monitoring & Observability**: Error handling, audit logging, system monitoring
- **♿ Accessibility & UX**: Accessible components, design system
- **🧪 Testing & Quality**: Unit, integration, and E2E tests

## 🔗 **API Endpoints**

### Essential VAPI Endpoints
- `POST /webhooks/incoming_call` - VAPI webhook handler ⭐
- `GET /appointments/availability` - Check appointment availability
- `POST /appointments/book` - Book new appointment
- `POST /appointments/cancel` - Cancel appointment

### Authentication
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - User logout

### Clinic Management
- `GET /clinics` - List clinics
- `POST /clinics` - Create clinic
- `PUT /clinics/{id}` - Update clinic
- `DELETE /clinics/{id}` - Delete clinic

## 🗄️ **Database Schema**

The system uses a comprehensive database schema with the following key tables:

- **Users** - System users and authentication
- **Clinics** - Healthcare practice information
- **Assistants** - AI assistant configurations
- **Calls** - VAPI call records and analytics ⭐
- **Appointments** - Patient appointments
- **Patients** - Patient information
- **AuditLogs** - HIPAA compliance logging

## 🚀 **Deployment**

### Docker Deployment
```bash
# Development
docker-compose --profile dev up -d

# Production
docker-compose --profile prod up -d

# Production with SSL
docker-compose --profile ssl up -d
```

### Environment Variables
```bash
# Required
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
VAPI_API_KEY=your_vapi_key
GOOGLE_CALENDAR_ID=your_calendar_id

# Optional
ENVIRONMENT=development
LOG_LEVEL=info
JWT_SECRET=your_jwt_secret
```

## 📊 **Monitoring**

The system includes comprehensive monitoring with:
- **Prometheus** - Metrics collection
- **Grafana** - Dashboards and visualization
- **Health Checks** - Application health monitoring
- **Audit Logging** - HIPAA compliance

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

For support and questions:
- 📧 Email: team@healthcarevoiceai.com
- 🐛 Issues: [GitHub Issues](https://github.com/dental-voice-ai/dental-voice-ai/issues)
- 📖 Documentation: [docs/](docs/)

---

**Built with ❤️ for healthcare practices**