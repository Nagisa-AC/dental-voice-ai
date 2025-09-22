# Healthcare Voice AI - Development and Deployment Makefile
# Comprehensive automation for development, testing, and deployment

.PHONY: help install dev prod test clean build deploy logs status health

# Default target
help: ## Show this help message
	@echo "Healthcare Voice AI - Available Commands:"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development Commands
install: ## Install all dependencies
	@echo "🔧 Installing dependencies..."
	pip install -e ".[dev]"
	cd frontend && npm install

dev: ## Start development environment
	@echo "🚀 Starting development environment..."
	docker-compose --profile dev up -d
	@echo "✅ Development environment started"
	@echo "📱 Frontend: http://localhost:3000"
	@echo "🔧 Backend: http://localhost:8000"
	@echo "📊 API Docs: http://localhost:8000/docs"

dev-logs: ## View development logs
	docker-compose --profile dev logs -f

dev-stop: ## Stop development environment
	docker-compose --profile dev down

# Production Commands
prod: ## Start production environment
	@echo "🏭 Starting production environment..."
	docker-compose --profile prod up -d
	@echo "✅ Production environment started"

prod-ssl: ## Start production environment with SSL
	@echo "🔒 Starting production environment with SSL..."
	docker-compose --profile ssl up -d
	@echo "✅ Production environment with SSL started"

prod-logs: ## View production logs
	docker-compose --profile prod logs -f

prod-stop: ## Stop production environment
	docker-compose --profile prod down

# Testing Commands
test: ## Run all tests
	@echo "🧪 Running all tests..."
	pytest tests/ -v --cov=src.healthcare_voice_ai --cov-report=html --cov-report=term

test-unit: ## Run unit tests
	@echo "🧪 Running unit tests..."
	pytest tests/unit/ -v

test-integration: ## Run integration tests
	@echo "🧪 Running integration tests..."
	pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests
	@echo "🧪 Running end-to-end tests..."
	pytest tests/e2e/ -v

test-frontend: ## Run frontend tests
	@echo "🧪 Running frontend tests..."
	cd frontend && npm test -- --coverage --watchAll=false

test-coverage: ## Generate test coverage report
	@echo "📊 Generating coverage report..."
	pytest tests/ --cov=src.healthcare_voice_ai --cov-report=html --cov-report=term
	@echo "📊 Coverage report generated in htmlcov/"

# Code Quality Commands
lint: ## Run linting
	@echo "🔍 Running linting..."
	pre-commit run --all-files

lint-fix: ## Fix linting issues
	@echo "🔧 Fixing linting issues..."
	pre-commit run --all-files --hook-stage manual

format: ## Format code
	@echo "🎨 Formatting code..."
	black src/ tests/
	isort src/ tests/
	cd frontend && npm run format

type-check: ## Run type checking
	@echo "🔍 Running type checking..."
	mypy src/
	cd frontend && npm run type-check

security: ## Run security checks
	@echo "🔒 Running security checks..."
	bandit -r src/ -f json -o bandit-report.json
	@echo "🔒 Security report generated: bandit-report.json"

# Build Commands
build: ## Build all components
	@echo "🏗️ Building all components..."
	docker-compose build
	cd frontend && npm run build

build-prod: ## Build production images
	@echo "🏗️ Building production images..."
	docker-compose build --target production

build-frontend: ## Build frontend
	@echo "🏗️ Building frontend..."
	cd frontend && npm run build

# Database Commands
db-migrate: ## Run database migrations
	@echo "🗄️ Running database migrations..."
	python3 -m alembic upgrade head

db-rollback: ## Rollback database migrations
	@echo "🗄️ Rolling back database migrations..."
	python3 -m alembic downgrade -1

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "🗄️ Resetting database..."
	@echo "⚠️  WARNING: This will destroy all data!"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ]
	python3 scripts/reset_database.py --confirm

db-reset-seed: ## Reset database and seed with test data
	@echo "🗄️ Resetting database with test data..."
	python3 scripts/reset_database.py --seed --confirm

db-status: ## Check database migration status
	@echo "🗄️ Database migration status:"
	python3 -m alembic current

db-history: ## Show database migration history
	@echo "🗄️ Database migration history:"
	python3 -m alembic history

db-backup: ## Backup database
	@echo "💾 Backing up database..."
	@mkdir -p backups
	@cp dental_voice_ai.db backups/backup_$(shell date +%Y%m%d_%H%M%S).db
	@echo "💾 Database backup completed"

db-schema: ## Generate database schema documentation
	@echo "📋 Generating database schema..."
	python3 scripts/generate_schema.py --format sql --output scripts/database_schema.sql
	python3 scripts/generate_schema.py --format markdown --output docs/DATABASE_SCHEMA.md
	python3 scripts/generate_schema.py --format json --output docs/database_schema.json
	@echo "✅ Database schema documentation generated"

# Monitoring Commands
monitoring: ## Start monitoring stack
	@echo "📊 Starting monitoring stack..."
	docker-compose --profile monitoring up -d
	@echo "✅ Monitoring stack started"
	@echo "📊 Prometheus: http://localhost:9090"
	@echo "📈 Grafana: http://localhost:3000"

monitoring-logs: ## View monitoring logs
	docker-compose --profile monitoring logs -f

monitoring-stop: ## Stop monitoring stack
	docker-compose --profile monitoring down

# Deployment Commands
deploy-staging: ## Deploy to staging
	@echo "🚀 Deploying to staging..."
	docker-compose --profile dev up -d
	@echo "✅ Staging deployment completed"

deploy-prod: ## Deploy to production
	@echo "🚀 Deploying to production..."
	docker-compose --profile ssl --profile monitoring up -d
	@echo "✅ Production deployment completed"

# Utility Commands
logs: ## View application logs
	docker-compose logs -f app

status: ## Check application status
	@echo "📊 Application Status:"
	@echo "===================="
	@docker-compose ps
	@echo ""
	@echo "🔍 Health Check:"
	@curl -s http://localhost:8000/health | jq . || echo "Health check failed"

health: ## Check system health
	@echo "🏥 System Health Check:"
	@echo "======================"
	@curl -s http://localhost:8000/system/health | jq . || echo "Health check failed"

clean: ## Clean up Docker resources
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

clean-all: ## Clean up all resources including images
	@echo "🧹 Cleaning up all Docker resources..."
	docker-compose down -v --rmi all
	docker system prune -a -f
	docker volume prune -f

# SSL Commands
ssl-setup: ## Setup SSL certificates
	@echo "🔒 Setting up SSL certificates..."
	docker-compose exec nginx-ssl certbot --nginx -d your-domain.com

ssl-renew: ## Renew SSL certificates
	@echo "🔒 Renewing SSL certificates..."
	docker-compose exec nginx-ssl certbot renew

ssl-status: ## Check SSL certificate status
	@echo "🔒 SSL Certificate Status:"
	docker-compose exec nginx-ssl certbot certificates

# Backup Commands
backup: ## Create full backup
	@echo "💾 Creating full backup..."
	@mkdir -p backups
	@tar -czf backups/healthcare-ai-backup-$(shell date +%Y%m%d_%H%M%S).tar.gz uploads/ logs/ quarantine/
	@echo "💾 Backup completed"

restore: ## Restore from backup (usage: make restore BACKUP_FILE=backup.tar.gz)
	@echo "💾 Restoring from backup: $(BACKUP_FILE)"
	@tar -xzf $(BACKUP_FILE)
	@echo "💾 Restore completed"

# Development Setup
setup: ## Initial development setup
	@echo "🚀 Setting up development environment..."
	@cp .env.example .env
	@echo "📝 Please edit .env file with your configuration"
	@make install
	@make dev
	@echo "✅ Development environment setup completed"

# Quick Commands
start: dev ## Alias for dev
stop: dev-stop ## Alias for dev-stop
restart: dev-stop dev ## Restart development environment

# Environment-specific commands
dev-full: ## Start full development stack with monitoring
	docker-compose --profile dev --profile monitoring up -d

prod-full: ## Start full production stack
	docker-compose --profile ssl --profile monitoring up -d

# Performance Commands
perf-test: ## Run performance tests
	@echo "⚡ Running performance tests..."
	# Add performance testing commands here

load-test: ## Run load tests
	@echo "⚡ Running load tests..."
	# Add load testing commands here

# Security Commands
security-scan: ## Run comprehensive security scan
	@echo "🔒 Running comprehensive security scan..."
	@make security
	@echo "🔒 Running dependency vulnerability scan..."
	cd frontend && npm audit
	@echo "🔒 Security scan completed"

# Documentation Commands
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	# Add documentation generation commands here

docs-serve: ## Serve documentation locally
	@echo "📚 Serving documentation..."
	# Add documentation serving commands here

# Maintenance Commands
update: ## Update dependencies
	@echo "🔄 Updating dependencies..."
	pip install --upgrade -e ".[dev]"
	cd frontend && npm update

update-docker: ## Update Docker images
	@echo "🔄 Updating Docker images..."
	docker-compose pull
	docker-compose up -d

# Health and Monitoring
metrics: ## View application metrics
	@echo "📊 Application Metrics:"
	@curl -s http://localhost:8000/metrics | head -20

alerts: ## Check for alerts
	@echo "🚨 Checking for alerts..."
	@curl -s http://localhost:8000/system/status | jq '.alerts' || echo "No alerts"

# Quick Status Check
quick-status: ## Quick status check
	@echo "⚡ Quick Status Check:"
	@echo "====================="
	@docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@curl -s http://localhost:8000/health | jq '.status' || echo "❌ Unhealthy"