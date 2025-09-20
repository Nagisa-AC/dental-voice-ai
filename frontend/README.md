# Healthcare Voice AI - React Frontend

A modern React TypeScript frontend for the Healthcare Voice AI application, built with Material-UI and Recharts.

## Features

- 🎨 **Modern UI**: Built with Material-UI (MUI) for a professional, responsive design
- 📊 **Interactive Charts**: Real-time data visualization with Recharts
- 🔐 **Authentication**: Secure login with JWT token management
- 📱 **Responsive**: Mobile-first design that works on all devices
- ⚡ **Fast**: Optimized React components with TypeScript
- 🎯 **Dashboard**: Comprehensive overview of healthcare practice metrics

## Tech Stack

- **React 19** with TypeScript
- **Material-UI (MUI)** for UI components
- **Recharts** for data visualization
- **React Router** for navigation
- **Axios** for API communication
- **Context API** for state management

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The app will open at http://localhost:3000

### Building for Production

```bash
# Build the app
npm run build

# The build folder will be created with optimized production files
```

## Project Structure

```
src/
├── components/           # React components
│   ├── dashboard/       # Dashboard-specific components
│   ├── Dashboard.tsx    # Main dashboard component
│   └── Login.tsx        # Login component
├── contexts/            # React contexts
│   └── AuthContext.tsx  # Authentication context
├── api/                 # API configuration
│   └── axios.ts         # Axios setup
└── App.tsx              # Main app component
```

## Components

### Dashboard Components

- **OverviewCard**: Displays key metrics with icons and trends
- **AppointmentsChart**: Line chart showing appointment trends
- **PatientsChart**: Pie chart showing patient engagement levels
- **RevenueChart**: Bar chart displaying revenue analysis
- **AIPerformanceChart**: Line chart tracking AI performance metrics
- **HealthStatus**: System health monitoring component

### Authentication

The app uses JWT tokens for authentication:
- Login credentials are stored securely
- Automatic token refresh
- Protected routes
- Logout functionality

## API Integration

The frontend communicates with the FastAPI backend:
- Base URL: `http://localhost:8000`
- Authentication: Bearer token in headers
- Error handling: Automatic token refresh on 401 errors

## Development

### Available Scripts

- `npm start`: Start development server
- `npm run build`: Build for production
- `npm test`: Run tests
- `npm run eject`: Eject from Create React App

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

## Deployment

1. Build the React app: `npm run build`
2. The backend will serve the built files from `frontend/build/`
3. Configure your web server to serve the React app for all non-API routes

## Contributing

1. Follow TypeScript best practices
2. Use Material-UI components consistently
3. Write tests for new components
4. Follow the existing code structure

## License

This project is part of the Dental Voice AI application.