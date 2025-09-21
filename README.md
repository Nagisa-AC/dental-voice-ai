# Healthcare Voice AI 🏥

[![CI](https://github.com/healthcare-voice-ai/healthcare-voice-ai/workflows/CI/badge.svg)](https://github.com/healthcare-voice-ai/healthcare-voice-ai/actions)
[![Coverage](https://codecov.io/gh/healthcare-voice-ai/healthcare-voice-ai/branch/main/graph/badge.svg)](https://codecov.io/gh/healthcare-voice-ai/healthcare-voice-ai)
[![Docker](https://img.shields.io/docker/pulls/healthcarevoiceai/healthcare-voice-ai)](https://hub.docker.com/r/healthcarevoiceai/healthcare-voice-ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)

**AI-powered voice assistants for healthcare practices with VAPI integration.**

## 🚀 Features

- **🏥 Multi-Specialty Support**: Dental, medical, mental health, veterinary, and more
- **🤖 VAPI Integration**: Seamless integration with VAPI voice AI platform
- **🎯 Webhook Processing**: Minimal webhook endpoints for VAPI availability checking
- **🔧 Production-Ready API**: FastAPI backend with comprehensive error handling
- **📚 Industry-Specific Prompts**: Customized AI responses for different healthcare specialties
- **🏥 Healthcare Compliant**: Built with HIPAA and healthcare workflows in mind

## 🏥 Supported Healthcare Specialties

- **🦷 Dental Practices**: General dentistry, orthodontics, oral surgery
- **🏥 Medical Clinics**: Family medicine, internal medicine, pediatrics
- **🧠 Mental Health**: Therapy, counseling, psychiatry
- **🦴 Specialists**: Cardiology, dermatology, orthopedics, chiropractic
- **🐾 Veterinary**: Animal hospitals, veterinary clinics

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   VAPI Voice    │    │   FastAPI       │
│   Assistant     │◄──►│   Backend       │
│   (Riley)       │    │   (Python)      │
└─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Google        │    │   Prompt        │
│   Calendar      │    │   Library       │
│   (Events)      │    │   (Markdown)    │
└─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Supabase account
- VAPI account
- Google Calendar API access

### Installation

#### Quick Setup (Recommended)

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

#### Manual Setup

```bash
# Clone the repository
git clone https://github.com/dental-voice-ai/dental-voice-ai.git
cd dental-voice-ai

# Copy environment template
cp .env.example .env
# Edit .env with your configuration

# Install dependencies
pip install -e ".[dev]"
cd frontend && npm install && cd ..

# Start with Docker (recommended)
# Development environment
docker compose --profile dev up -d

# Production environment
docker compose --profile prod up -d

# Production with SSL/TLS
docker compose --profile ssl up -d

# Or run locally
uvicorn src.healthcare_voice_ai.main:app --reload

# Run tests
python -m pytest tests/ -v
```

### Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Configure your environment variables
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
VAPI_API_KEY=your_vapi_key
GOOGLE_CALENDAR_ID=your_calendar_id
```

## 📚 Documentation

- **[API Reference](docs/API.md)** - Complete API documentation
- **[Prompt Management](prompts/dental_assistant.md)** - VAPI assistant prompts
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Contributing](CONTRIBUTING.md)** - Development guidelines

## 🗺️ Development Roadmap

### Phase 1: Foundation (Q4 2025) ✅
**Status**: In Progress
**Target**: Production-ready core system

- [x] **Core Architecture**
  - [x] FastAPI backend with production standards
  - [x] Supabase database integration
  - [x] VAPI voice assistant integration
  - [x] Google Calendar API integration

- [x] **Basic Appointment Management**
  - [x] Appointment booking via voice
  - [x] Calendar availability checking
  - [x] Database storage and retrieval
  - [x] Basic error handling

- [x] **Development Infrastructure**
  - [x] Docker containerization
  - [x] CI/CD pipeline setup
  - [x] Code quality tools (linting, formatting)
  - [x] Test framework and coverage

### Phase 2: Enhancement (Q1 2026) 🚧
**Status**: Planning
**Target**: Advanced features and integrations

- [ ] **Advanced Appointment Features**
  - [ ] Appointment rescheduling via voice
  - [ ] Appointment cancellation with confirmation
  - [ ] Recurring appointment support
  - [ ] Waitlist management
  - [ ] Appointment reminders (SMS/email)

- [ ] **Patient Management**
  - [ ] Patient profile creation and management
  - [ ] Medical history tracking
  - [ ] Insurance information storage
  - [ ] Patient preferences and notes
  - [ ] HIPAA compliance enhancements

- [ ] **Multi-Practice Support**
  - [ ] Multi-tenant architecture
  - [ ] Practice-specific configurations
  - [ ] Role-based access control
  - [ ] Practice analytics dashboard

### Phase 3: Intelligence (Q2 2026) 📋
**Status**: Research
**Target**: AI-powered insights and automation

- [ ] **Intelligent Scheduling**
  - [ ] AI-powered appointment optimization
  - [ ] Predictive no-show detection
  - [ ] Smart time slot recommendations
  - [ ] Dynamic scheduling based on urgency

- [ ] **Voice AI Enhancements**
  - [ ] Multi-language support (Spanish, French)
  - [ ] Accent and dialect recognition
  - [ ] Context-aware conversations
  - [ ] Emotional intelligence features

- [ ] **Analytics and Reporting**
  - [ ] Practice performance metrics
  - [ ] Patient satisfaction tracking
  - [ ] Revenue optimization insights
  - [ ] Predictive analytics dashboard

## 🏗️ Project Structure

### Backend Architecture
```
src/healthcare_voice_ai/
├── api/v1/                    # API endpoints
│   ├── auth.py               # Authentication
│   ├── clinic.py             # Clinic management
│   ├── webhooks.py           # VAPI webhooks
│   ├── system.py             # System monitoring (consolidated)
│   ├── audit.py              # Audit logging
│   └── file_upload.py        # File upload
├── core/                     # Core business logic
│   ├── config.py             # Configuration (consolidated)
│   ├── auth.py               # Authentication logic
│   ├── database.py           # Database management (with performance indexes)
│   ├── security.py           # Security utilities
│   ├── models/               # Database models
│   ├── services/             # Business services
│   ├── middleware/           # Custom middleware
│   └── utils/                # Utility functions (with input validation)
└── utils/                    # Utility functions
```

### Frontend Architecture
```
frontend/src/
├── common/                   # Shared components
│   ├── components/           # Reusable components
│   │   ├── DesignSystem/     # Design system (with accessibility)
│   │   └── ErrorBoundary.tsx # Error boundary
│   ├── contexts/             # React contexts
│   ├── hooks/                # Custom hooks
│   └── utils/                # Utility functions
├── features/                 # Feature modules
│   ├── auth/                 # Authentication
│   ├── dashboard/            # Dashboard
│   └── landing/              # Landing page
├── layouts/                  # Layout components
└── styles/                   # Global styles (with accessibility)
```

### Key Features
- **🔐 Security & Authentication**: JWT auth, CSRF protection, HTTPS enforcement
- **🏥 Healthcare Business Logic**: Clinic management, AI assistant integration
- **📊 Monitoring & Observability**: Error handling, audit logging, system monitoring
- **♿ Accessibility & UX**: Accessible components, design system
- **🧪 Testing & Quality**: Unit, integration, and E2E tests

## 🎯 Core Components

### 1. Voice Assistant (Riley)
- **Role**: AI dental office assistant
- **Capabilities**: Patient inquiries, appointment management, calendar integration
- **Integration**: VAPI platform with Google Calendar and direct API calls

### 2. Backend API
- **Framework**: FastAPI with Python 3.9
- **Endpoints**: Webhook availability checking
- **Purpose**: Minimal webhook processor for VAPI integration

### 3. Prompt Library
- **Format**: Markdown with YAML front-matter
- **Validation**: JSON Schema enforcement
- **Versioning**: Semantic versioning for prompts
- **Tools**: VAPI tool integration for calendar and database operations

### 4. Calendar Integration
- **Provider**: Google Calendar API
- **Features**: Real-time availability checking, event creation/updates
- **Timezone**: Full Chicago timezone support (CST/CDT)

## 🔧 Development

### Project Structure

```
dental-voice-ai/
├── src/dental_voice_ai/     # Application code
│   ├── api/                 # FastAPI endpoints
│   ├── config/              # Pydantic settings
│   ├── domain/              # Business logic
│   ├── adapters/            # External integrations
│   └── utils/               # Utilities
├── prompts/                 # VAPI prompt library
│   ├── core/                # System prompts
│   ├── tasks/               # Task-specific prompts
│   ├── examples/            # Sample conversations
│   └── schemas/             # JSON schemas
├── tests/                   # Test suite
├── docs/                    # Documentation
├── scripts/                 # CLI tools
└── .github/workflows/       # CI/CD pipelines
```

### Key Commands

```bash
# Development
pip install -e ".[dev]"          # Install dependencies
uvicorn src.healthcare_voice_ai.main:app --reload  # Start dev server
python -m pytest tests/ -v       # Run test suite
python -m ruff check src/ tests/  # Code linting
python -m black src/ tests/       # Code formatting
python -m isort src/ tests/       # Import sorting

# Prompt Management
# Edit prompts in prompts/ directory and copy to VAPI

# Docker
docker build -t healthcare-voice-ai .  # Build Docker image

# Development
docker compose --profile dev up -d

# Production
docker compose --profile prod up -d

# Production with SSL
docker compose --profile ssl up -d

# Testing
docker compose --profile test up --abort-on-container-exit

# Monitoring
docker compose --profile monitoring up -d
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dental_voice_ai

# Run specific test categories
pytest -m unit        # Unit tests
pytest -m integration # Integration tests
pytest -m slow        # Slow tests
```

## 🚀 Deployment

### Docker Profiles

The project uses Docker Compose profiles to support different environments:

- **`dev`**: Development environment with hot reload, debug logging, and local volumes
- **`prod`**: Production environment with optimized settings and nginx reverse proxy
- **`ssl`**: Production environment with SSL/TLS termination and automatic certificate renewal
- **`test`**: Testing environment for running automated tests
- **`monitoring`**: Monitoring stack with Prometheus and Grafana
- **`migrate`**: Database migration service
- **`backup`**: Backup service

### Docker Deployment

```bash
# Production deployment (without SSL)
docker compose --profile prod up -d

# Production deployment (with SSL/TLS)
docker compose --profile ssl up -d

# Health check
curl http://localhost:8000/health

# View logs
docker compose logs -f app-prod
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | ✅ |
| `SUPABASE_KEY` | Supabase service key | ✅ |
| `VAPI_API_KEY` | VAPI API key | ✅ |
| `GOOGLE_CALENDAR_ID` | Google Calendar ID | ✅ |
| `ENVIRONMENT` | Environment (dev/prod) | ✅ |
| `LOG_LEVEL` | Logging level | ❌ |

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Fork and clone
git clone https://github.com/your-username/dental-voice-ai.git
cd dental-voice-ai

# Install pre-commit hooks
pre-commit install

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and test
python -m pytest tests/ -v
python -m ruff check src/ tests/

# Commit with conventional commits
git commit -m "feat: add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.dentalvoiceai.com](https://docs.dentalvoiceai.com)
- **Issues**: [GitHub Issues](https://github.com/dental-voice-ai/dental-voice-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dental-voice-ai/dental-voice-ai/discussions)
- **Email**: support@dentalvoiceai.com

## 🙏 Acknowledgments

- [VAPI](https://vapi.ai) for voice AI platform
- [Supabase](https://supabase.com) for backend-as-a-service
- [FastAPI](https://fastapi.tiangolo.com) for the web framework
- [Google Calendar API](https://developers.google.com/calendar) for calendar integration

---

**Made with ❤️ for dental practices everywhere**
