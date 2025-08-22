# Dental Voice AI 🦷

[![CI](https://github.com/dental-voice-ai/dental-voice-ai/workflows/CI/badge.svg)](https://github.com/dental-voice-ai/dental-voice-ai/actions)
[![Coverage](https://codecov.io/gh/dental-voice-ai/dental-voice-ai/branch/main/graph/badge.svg)](https://codecov.io/gh/dental-voice-ai/dental-voice-ai)
[![Docker](https://img.shields.io/docker/pulls/dentalvoiceai/dental-voice-ai)](https://hub.docker.com/r/dentalvoiceai/dental-voice-ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)

**AI-powered dental appointment management system with VAPI integration for seamless voice interactions and automated scheduling.**

## 🚀 Features

- **🤖 Intelligent Voice Assistant**: Riley, your AI dental office assistant powered by VAPI
- **📅 Automated Appointment Management**: Book, reschedule, and cancel appointments via voice
- **🗓️ Google Calendar Integration**: Real-time calendar synchronization and availability checking
- **💾 Supabase Database**: Robust data storage with real-time updates
- **🔧 Production-Ready API**: FastAPI backend with comprehensive error handling
- **📚 Simple Prompt Management**: Clean markdown files for VAPI assistant prompts
- **🏥 Healthcare Compliant**: Built with dental practice workflows in mind
- **🌐 Multi-Timezone Support**: Full Chicago timezone handling (CST/CDT)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   VAPI Voice    │    │   FastAPI       │    │   Supabase      │
│   Assistant     │◄──►│   Backend       │◄──►│   Database      │
│   (Riley)       │    │   (Python)      │    │   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Google        │    │   Prompt        │    │   Appointment   │
│   Calendar      │    │   Library       │    │   Management    │
│   (Events)      │    │   (Markdown)    │    │   (Business)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Supabase account
- VAPI account
- Google Calendar API access

### Installation

```bash
# Clone the repository
git clone https://github.com/dental-voice-ai/dental-voice-ai.git
cd dental-voice-ai

# Start with Docker (recommended)
docker compose up -d

# Or install locally
pip install -e ".[dev]"
python -m dental_voice_ai.main

# Run tests
python -m pytest tests/ -v

# Validate prompts
python scripts/validate_prompts.py
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

- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and C4 diagrams
- **[API Reference](docs/API.md)** - Complete API documentation
- **[Prompt Management](prompts/dental_assistant_prompts.md)** - VAPI assistant prompts
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Contributing](CONTRIBUTING.md)** - Development guidelines

## 🎯 Core Components

### 1. Voice Assistant (Riley)
- **Role**: AI dental office assistant
- **Capabilities**: Appointment booking, patient inquiries, calendar management
- **Integration**: VAPI platform with Google Calendar and Supabase

### 2. Backend API
- **Framework**: FastAPI with Python 3.11
- **Endpoints**: Appointment management, availability checking, data storage
- **Database**: Supabase (PostgreSQL) with real-time subscriptions

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
python -m pytest tests/ -v       # Run test suite
python -m ruff check src/ tests/  # Code linting
python -m black src/ tests/       # Code formatting
python -m isort src/ tests/       # Import sorting
python -m mkdocs build            # Build documentation

# Prompt Management
# Edit prompts in prompts/ directory and copy to VAPI

# Docker
docker build -t dental-voice-ai .  # Build Docker image
docker compose up -d               # Run with Docker Compose
docker compose run --rm app python -m pytest tests/ -v  # Run tests in Docker
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

### Docker Deployment

```bash
# Production deployment
docker compose -f docker-compose.prod.yml up -d

# Health check
curl http://localhost:8000/health
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
