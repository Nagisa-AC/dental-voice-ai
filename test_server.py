"""
Simple test server to serve the admin dashboard
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import os

app = FastAPI(title="Healthcare Voice AI - Admin Dashboard")

# Serve static files if they exist
if os.path.exists("frontend/build/static"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Healthcare Voice AI Server is running!", "admin_dashboard": "/admin"}

@app.get("/admin")
async def admin_dashboard():
    """Serve the admin dashboard"""
    if os.path.exists("frontend/build/index.html"):
        return FileResponse("frontend/build/index.html")
    else:
        # Return a simple HTML page for the admin dashboard
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Healthcare Voice AI - Admin Dashboard</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #0a0a0a;
                    color: #ffffff;
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                .header {
                    text-align: center;
                    margin-bottom: 40px;
                }
                .header h1 {
                    color: #00d4aa;
                    font-size: 2.5rem;
                    margin-bottom: 10px;
                }
                .header p {
                    color: #a0a0a0;
                    font-size: 1.2rem;
                }
                .dashboard-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }
                .card {
                    background: #1e1e1e;
                    border: 1px solid #333333;
                    border-radius: 8px;
                    padding: 24px;
                    transition: all 0.2s ease;
                }
                .card:hover {
                    border-color: #444444;
                    transform: translateY(-2px);
                }
                .card h3 {
                    color: #00d4aa;
                    margin-top: 0;
                }
                .metric {
                    text-align: center;
                    padding: 20px;
                }
                .metric-value {
                    font-size: 2rem;
                    font-weight: bold;
                    color: #00d4aa;
                    margin-bottom: 8px;
                }
                .metric-label {
                    color: #a0a0a0;
                    font-size: 0.9rem;
                }
                .status {
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 0.8rem;
                    font-weight: 600;
                    text-transform: uppercase;
                }
                .status-success {
                    background: rgba(0, 212, 170, 0.1);
                    color: #00d4aa;
                }
                .btn {
                    background: #00d4aa;
                    color: #0a0a0a;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-weight: 600;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                    transition: all 0.2s ease;
                }
                .btn:hover {
                    background: #00b894;
                }
                .info-box {
                    background: #1a1a1a;
                    border: 1px solid #333333;
                    border-radius: 8px;
                    padding: 20px;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 Healthcare Voice AI</h1>
                    <p>Admin Dashboard</p>
                </div>

                <div class="dashboard-grid">
                    <div class="card metric">
                        <div class="metric-value">12</div>
                        <div class="metric-label">Active Tenants</div>
                    </div>
                    <div class="card metric">
                        <div class="metric-value">2,847</div>
                        <div class="metric-label">Total Calls Today</div>
                    </div>
                    <div class="card metric">
                        <div class="metric-value">94.2%</div>
                        <div class="metric-label">Success Rate</div>
                    </div>
                    <div class="card metric">
                        <div class="metric-value">$24,580</div>
                        <div class="metric-label">Monthly Revenue</div>
                    </div>
                </div>

                <div class="dashboard-grid">
                    <div class="card">
                        <h3>📊 System Status</h3>
                        <p><span class="status status-success">✓ All Systems Operational</span></p>
                        <ul style="color: #a0a0a0; margin-top: 15px;">
                            <li>API Gateway: 99.9% uptime</li>
                            <li>Database: 99.8% uptime</li>
                            <li>Voice AI Service: 99.7% uptime</li>
                            <li>Google Calendar API: 98.5% uptime</li>
                        </ul>
                    </div>
                    <div class="card">
                        <h3>🔔 Recent Activity</h3>
                        <ul style="color: #a0a0a0;">
                            <li>New tenant registered - 2 minutes ago</li>
                            <li>High CPU usage detected - 15 minutes ago</li>
                            <li>Payment processed - 1 hour ago</li>
                            <li>Assistant updated - 2 hours ago</li>
                        </ul>
                    </div>
                </div>

                <div class="info-box">
                    <h3>🎯 Admin Dashboard Features</h3>
                    <p>This is a preview of your admin dashboard. The full React application includes:</p>
                    <ul>
                        <li>✨ Elegant dark theme inspired by ngrok design</li>
                        <li>📊 Real-time system metrics and KPIs</li>
                        <li>🏢 Comprehensive tenant management interface</li>
                        <li>👥 User management with role-based access control</li>
                        <li>🤖 Voice AI assistant management</li>
                        <li>📡 System monitoring and health checks</li>
                        <li>💳 Billing and subscription management</li>
                        <li>🔒 Security controls and audit logs</li>
                        <li>📈 Analytics and reporting</li>
                        <li>⚙️ System configuration and settings</li>
                    </ul>
                    <p><strong>To see the full React dashboard:</strong></p>
                    <ol>
                        <li>Run <code>cd frontend && npm run build</code></li>
                        <li>Restart the server</li>
                        <li>Visit <a href="/admin" style="color: #00d4aa;">/admin</a> again</li>
                    </ol>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

@app.get("/dashboard")
async def regular_dashboard():
    """Serve the regular dashboard"""
    return {"message": "Regular dashboard endpoint", "admin_dashboard": "/admin"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
