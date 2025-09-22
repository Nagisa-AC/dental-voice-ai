#!/usr/bin/env python3
"""
API Endpoints Lister for Healthcare Voice AI

This script extracts and lists all API endpoints from the FastAPI application.
Shows routes, methods, authentication requirements, and descriptions.

Usage:
    python scripts/list_endpoints.py [--format table|json|markdown]
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

from backend.main import app


def extract_endpoints() -> List[Dict[str, Any]]:
    """Extract all endpoints from the FastAPI app."""
    endpoints = []
    
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            # Skip static file routes
            if route.path.startswith('/static'):
                continue
                
            # Get route information
            methods = list(route.methods)
            path = route.path
            name = getattr(route, 'name', '')
            
            # Determine authentication requirement
            auth_required = "❌"
            admin_required = "❌"
            
            # Check if route has dependencies
            if hasattr(route, 'depend') and route.depend:
                for dep in route.depend:
                    dep_str = str(dep)
                    if 'get_current_user' in dep_str:
                        auth_required = "✅"
                    if 'require_admin' in dep_str:
                        admin_required = "✅"
            
            # Get route tags
            tags = []
            if hasattr(route, 'tags') and route.tags:
                tags = route.tags
            
            # Get route summary/description
            summary = ""
            if hasattr(route, 'summary') and route.summary:
                summary = route.summary
            
            # Determine category from path
            category = "General"
            if path.startswith('/auth'):
                category = "Authentication"
            elif path.startswith('/clinics'):
                category = "Clinic Management"
            elif path.startswith('/webhooks'):
                category = "Webhook Processing"
            elif path.startswith('/upload'):
                category = "File Upload"
            elif path.startswith('/audit'):
                category = "Audit & Compliance"
            elif path.startswith('/system'):
                category = "System Monitoring"
            elif path.startswith('/dashboard'):
                category = "Static"
            elif path.startswith('/docs') or path.startswith('/redoc') or path.startswith('/openapi'):
                category = "Documentation"
            
            for method in methods:
                if method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']:
                    endpoints.append({
                        'method': method,
                        'path': path,
                        'name': name,
                        'summary': summary,
                        'category': category,
                        'tags': tags,
                        'auth_required': auth_required,
                        'admin_required': admin_required
                    })
    
    return sorted(endpoints, key=lambda x: (x['category'], x['path'], x['method']))


def format_as_table(endpoints: List[Dict[str, Any]]) -> str:
    """Format endpoints as a markdown table."""
    lines = [
        "# 🏥 Healthcare Voice AI - API Endpoints Summary",
        "",
        f"**Total Endpoints**: {len(endpoints)}",
        "",
        "| Method | Endpoint | Category | Auth | Admin | Description |",
        "|--------|----------|----------|------|-------|-------------|"
    ]
    
    for endpoint in endpoints:
        method = endpoint['method']
        path = endpoint['path']
        category = endpoint['category']
        auth = endpoint['auth_required']
        admin = endpoint['admin_required']
        summary = endpoint['summary'] or endpoint['name'] or '-'
        
        lines.append(f"| `{method}` | `{path}` | {category} | {auth} | {admin} | {summary} |")
    
    return "\n".join(lines)


def format_as_json(endpoints: List[Dict[str, Any]]) -> str:
    """Format endpoints as JSON."""
    return json.dumps({
        "total_endpoints": len(endpoints),
        "endpoints": endpoints
    }, indent=2)


def format_as_markdown(endpoints: List[Dict[str, Any]]) -> str:
    """Format endpoints as detailed markdown."""
    lines = [
        "# 🏥 Healthcare Voice AI - Complete API Endpoints",
        "",
        f"**Total Endpoints**: {len(endpoints)}",
        ""
    ]
    
    # Group by category
    categories = {}
    for endpoint in endpoints:
        category = endpoint['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(endpoint)
    
    for category, category_endpoints in categories.items():
        lines.extend([
            f"## {category}",
            "",
            "| Method | Endpoint | Auth | Admin | Description |",
            "|--------|----------|------|-------|-------------|"
        ])
        
        for endpoint in category_endpoints:
            method = endpoint['method']
            path = endpoint['path']
            auth = endpoint['auth_required']
            admin = endpoint['admin_required']
            summary = endpoint['summary'] or endpoint['name'] or '-'
            
            lines.append(f"| `{method}` | `{path}` | {auth} | {admin} | {summary} |")
        
        lines.append("")
    
    return "\n".join(lines)


def print_statistics(endpoints: List[Dict[str, Any]]):
    """Print endpoint statistics."""
    print("\n📊 **Endpoint Statistics:**")
    print("-" * 30)
    
    # Count by method
    methods = {}
    for endpoint in endpoints:
        method = endpoint['method']
        methods[method] = methods.get(method, 0) + 1
    
    print("**By HTTP Method:**")
    for method, count in sorted(methods.items()):
        print(f"  {method}: {count}")
    
    # Count by category
    categories = {}
    for endpoint in endpoints:
        category = endpoint['category']
        categories[category] = categories.get(category, 0) + 1
    
    print("\n**By Category:**")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count}")
    
    # Count authentication requirements
    auth_required = sum(1 for e in endpoints if e['auth_required'] == '✅')
    admin_required = sum(1 for e in endpoints if e['admin_required'] == '✅')
    public = len(endpoints) - auth_required
    
    print("\n**By Authentication:**")
    print(f"  Public: {public}")
    print(f"  Authenticated: {auth_required}")
    print(f"  Admin Only: {admin_required}")


def main():
    """Main function to handle command line arguments and list endpoints."""
    parser = argparse.ArgumentParser(description="List all API endpoints from the Healthcare Voice AI application")
    parser.add_argument(
        "--format", 
        choices=["table", "json", "markdown"], 
        default="table",
        help="Output format (default: table)"
    )
    parser.add_argument(
        "--output", 
        type=str,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--stats", 
        action="store_true",
        help="Show endpoint statistics"
    )
    
    args = parser.parse_args()
    
    try:
        # Extract endpoints
        endpoints = extract_endpoints()
        
        # Format output
        if args.format == "table":
            content = format_as_table(endpoints)
        elif args.format == "json":
            content = format_as_json(endpoints)
        elif args.format == "markdown":
            content = format_as_markdown(endpoints)
        
        # Output content
        if args.output:
            with open(args.output, 'w') as f:
                f.write(content)
            print(f"✅ Endpoints list saved to {args.output}")
        else:
            print(content)
        
        # Show statistics if requested
        if args.stats:
            print_statistics(endpoints)
            
    except Exception as e:
        print(f"❌ Error listing endpoints: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

