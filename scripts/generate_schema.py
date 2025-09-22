#!/usr/bin/env python3
"""
Database Schema Generator for Healthcare Voice AI

This script generates the complete database schema from SQLAlchemy models
and can output it in various formats (SQL, JSON, etc.).

Usage:
    python scripts/generate_schema.py [--format sql|json|markdown] [--output file]
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

from backend.db.models.database_models import Base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.schema import CreateTable, CreateIndex


def generate_sql_schema():
    """Generate SQL schema from SQLAlchemy models."""
    
    # Create a temporary SQLite engine for schema generation
    engine = create_engine("sqlite:///:memory:")
    
    # Generate CREATE TABLE statements
    create_statements = []
    
    # Add header
    create_statements.append("-- Healthcare Voice AI - Complete Database Schema")
    create_statements.append(f"-- Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    create_statements.append("-- This script represents the complete database structure")
    create_statements.append("")
    
    # Generate table creation statements
    for table in Base.metadata.tables.values():
        create_statements.append(f"-- =============================================================================")
        create_statements.append(f"-- {table.name.upper()} TABLE")
        create_statements.append(f"-- =============================================================================")
        
        # Create table statement
        create_table = CreateTable(table)
        create_statements.append(str(create_table.compile(engine)).strip() + ";")
        create_statements.append("")
        
        # Add indexes
        for index in table.indexes:
            if not index.unique:
                create_statements.append(f"CREATE INDEX {index.name} ON {table.name} ({', '.join([col.name for col in index.columns])});")
            else:
                create_statements.append(f"CREATE UNIQUE INDEX {index.name} ON {table.name} ({', '.join([col.name for col in index.columns])});")
        
        create_statements.append("")
    
    return "\n".join(create_statements)


def generate_json_schema():
    """Generate JSON schema representation."""
    
    schema = {
        "database": "healthcare_voice_ai",
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat(),
        "tables": {}
    }
    
    for table_name, table in Base.metadata.tables.items():
        table_info = {
            "name": table_name,
            "columns": {},
            "indexes": [],
            "foreign_keys": [],
            "primary_key": [col.name for col in table.primary_key.columns]
        }
        
        # Add columns
        for column in table.columns:
            column_info = {
                "type": str(column.type),
                "nullable": column.nullable,
                "default": str(column.default) if column.default else None,
                "unique": column.unique,
                "index": column.index
            }
            table_info["columns"][column.name] = column_info
        
        # Add indexes
        for index in table.indexes:
            index_info = {
                "name": index.name,
                "columns": [col.name for col in index.columns],
                "unique": index.unique
            }
            table_info["indexes"].append(index_info)
        
        # Add foreign keys
        for fk in table.foreign_keys:
            fk_info = {
                "column": fk.parent.name,
                "referenced_table": fk.column.table.name,
                "referenced_column": fk.column.name,
                "on_delete": fk.ondelete,
                "on_update": fk.onupdate
            }
            table_info["foreign_keys"].append(fk_info)
        
        schema["tables"][table_name] = table_info
    
    return json.dumps(schema, indent=2)


def generate_markdown_schema():
    """Generate Markdown documentation of the schema."""
    
    md_lines = [
        "# Healthcare Voice AI - Database Schema",
        "",
        f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
        "## Overview",
        "",
        "This document describes the complete database schema for the Healthcare Voice AI system.",
        "",
        "## Tables",
        ""
    ]
    
    for table_name, table in Base.metadata.tables.items():
        md_lines.extend([
            f"### {table_name.title()}",
            "",
            f"**Description**: {table.comment or 'No description available'}",
            "",
            "#### Columns",
            "",
            "| Column | Type | Nullable | Default | Unique | Index |",
            "|--------|------|----------|---------|--------|-------|"
        ])
        
        for column in table.columns:
            nullable = "Yes" if column.nullable else "No"
            default = str(column.default) if column.default else ""
            unique = "Yes" if column.unique else "No"
            index = "Yes" if column.index else "No"
            
            md_lines.append(f"| {column.name} | {column.type} | {nullable} | {default} | {unique} | {index} |")
        
        md_lines.extend([
            "",
            "#### Indexes",
            ""
        ])
        
        if table.indexes:
            for index in table.indexes:
                unique_text = " (UNIQUE)" if index.unique else ""
                md_lines.append(f"- **{index.name}**{unique_text}: {', '.join([col.name for col in index.columns])}")
        else:
            md_lines.append("*No custom indexes*")
        
        md_lines.extend([
            "",
            "#### Foreign Keys",
            ""
        ])
        
        if table.foreign_keys:
            for fk in table.foreign_keys:
                on_delete = f" ON DELETE {fk.ondelete}" if fk.ondelete else ""
                on_update = f" ON UPDATE {fk.onupdate}" if fk.onupdate else ""
                md_lines.append(f"- **{fk.parent.name}** → `{fk.column.table.name}.{fk.column.name}`{on_delete}{on_update}")
        else:
            md_lines.append("*No foreign keys*")
        
        md_lines.append("")
    
    # Add relationships section
    md_lines.extend([
        "## Relationships",
        "",
        "### Entity Relationship Diagram",
        "",
        "```mermaid",
        "erDiagram",
        ""
    ])
    
    # Generate Mermaid ERD
    for table_name, table in Base.metadata.tables.items():
        md_lines.append(f"    {table_name} {{")
        for column in table.columns:
            if column.primary_key:
                md_lines.append(f"        {column.name} {column.type} PK")
            elif column.foreign_keys:
                md_lines.append(f"        {column.name} {column.type} FK")
            else:
                md_lines.append(f"        {column.name} {column.type}")
        md_lines.append("    }")
        md_lines.append("")
    
    # Add relationships
    for table_name, table in Base.metadata.tables.items():
        for fk in table.foreign_keys:
            md_lines.append(f"    {table_name} ||--o{{ {fk.column.table.name} : {fk.parent.name}")
    
    md_lines.extend([
        "```",
        "",
        "## Indexes Summary",
        "",
        "| Table | Index Name | Columns | Type |",
        "|-------|------------|---------|------|"
    ])
    
    for table_name, table in Base.metadata.tables.items():
        for index in table.indexes:
            index_type = "UNIQUE" if index.unique else "INDEX"
            columns = ", ".join([col.name for col in index.columns])
            md_lines.append(f"| {table_name} | {index.name} | {columns} | {index_type} |")
    
    md_lines.extend([
        "",
        "## Performance Considerations",
        "",
        "- All foreign key columns are indexed for join performance",
        "- Composite indexes are created for common query patterns",
        "- Audit logs have time-based indexes for efficient querying",
        "- User authentication queries are optimized with email/role indexes",
        "- Clinic management queries use tenant_id and status indexes",
        "",
        "## Security Features",
        "",
        "- Comprehensive audit logging for HIPAA compliance",
        "- CSRF token management",
        "- Rate limiting with configurable windows",
        "- File quarantine system for security",
        "- Password hashing with bcrypt",
        "- JWT token rotation with refresh tokens"
    ])
    
    return "\n".join(md_lines)


def main():
    """Main function to handle command line arguments and generate schema."""
    parser = argparse.ArgumentParser(description="Generate database schema from SQLAlchemy models")
    parser.add_argument(
        "--format", 
        choices=["sql", "json", "markdown"], 
        default="sql",
        help="Output format (default: sql)"
    )
    parser.add_argument(
        "--output", 
        type=str,
        help="Output file path (default: stdout)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.format == "sql":
            content = generate_sql_schema()
        elif args.format == "json":
            content = generate_json_schema()
        elif args.format == "markdown":
            content = generate_markdown_schema()
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(content)
            print(f"✅ Schema generated and saved to {args.output}")
        else:
            print(content)
            
    except Exception as e:
        print(f"❌ Error generating schema: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

