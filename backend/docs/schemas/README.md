# Database Schemas & Data Models

This directory contains database schemas, SQL scripts, and data model documentation.

## 📁 Contents

### Database Schemas
- `database_schemas.sql` - Complete database schema
- `tables.md` - Table documentation
- `relationships.md` - Database relationships

### Data Models
- `pydantic_models.md` - Pydantic model documentation
- `api_schemas.md` - API request/response schemas

### Database Operations
- `queries.md` - Common database queries
- `indexes.md` - Database indexes and optimization

## 🗄️ Database Tables

### Core Tables
- `tenants` - Dental practice information
- `calls` - Call transcripts and analysis
- `appointment_requests` - Appointment bookings
- `office_availabilities` - Available time slots

### Key Features
- Multi-practice support via tenant_id
- Comprehensive call logging
- Appointment management
- Availability tracking

## 🚀 Setup

1. Run `database_schemas.sql` in Supabase
2. Verify table creation
3. Check indexes and constraints
4. Test data insertion

## 📝 Schema Changes

1. Update `database_schemas.sql`
2. Document changes in `tables.md`
3. Update Pydantic models if needed
4. Test with sample data
