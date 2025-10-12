# 🎨 Deepfake Detection Frontend

Modern React-based frontend for the Advanced Deepfake Detection System, built with TypeScript, Vite, and Tailwind CSS.

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** (20+ recommended)
- **npm** or **yarn**
- Backend server running on `http://localhost:8000`

### Installation
```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🛠️ Available Scripts

```bash
# Development server with hot reload
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🏗️ Project Structure

```
frontend/src/
├── components/          # Reusable UI components
│   ├── ui/             # shadcn/ui components
│   ├── auth/           # Authentication components
│   ├── admin/          # Admin dashboard components
│   └── three/          # Three.js 3D components
├── pages/              # Application pages
│   ├── TryIt.tsx       # Main detection interface
│   ├── AdminDashboard.tsx
│   ├── SystemStatus.tsx
│   └── ...
├── contexts/           # React contexts
│   ├── AuthContext.tsx
│   ├── PaymentContext.tsx
│   └── ...
├── hooks/              # Custom React hooks
├── lib/                # Utility libraries
├── services/           # API services
└── utils/              # Helper functions
```

## 🎯 Key Features

### Detection Interface
- **Drag & Drop Upload** with progress indicators
- **Real-time Camera** detection via WebSocket
- **YouTube URL** support for remote analysis
- **Three Detection Modes**: Traditional, Modern AI, Hybrid
- **Results Visualization** with confidence scores and detailed breakdowns

### Authentication System
- **JWT-based** authentication
- **Role-based Access Control** (Admin, Premium, Standard, Guest)
- **Secure Login/Register** forms
- **Access Request** system for premium features

### Admin Dashboard
- **System Monitoring** with real-time metrics
- **User Management** and access control
- **Detection Analytics** and statistics
- **Model Performance** tracking

### UI/UX Features
- **Responsive Design** (mobile-first)
- **Dark/Light Themes** with system preference detection
- **Smooth Animations** with Framer Motion
- **3D Visualizations** with Three.js
- **PDF Report Generation**
- **Accessibility** compliance (WCAG 2.1)

## 🔧 Configuration

### Environment Variables
Create `.env.local` with:

```env
# Backend API URL
VITE_API_URL=http://localhost:8000

# Development settings
VITE_DEBUG=true

# Optional: Custom app title
# VITE_APP_TITLE=Deepfake Detection System
```

### API Integration
The frontend communicates with the backend via:

- **REST API**: File uploads, user management, system status
- **WebSocket**: Real-time detection streaming
- **Authentication**: JWT tokens with refresh mechanism

## 🎨 Tech Stack

### Core Framework
- **React 18** with TypeScript
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing

### UI Framework
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Modern component library
- **Lucide React** - Beautiful icons
- **Framer Motion** - Smooth animations

### 3D Graphics
- **Three.js** - 3D graphics library
- **@react-three/fiber** - React renderer for Three.js
- **@react-three/drei** - Useful helpers for Three.js

### State Management
- **React Context** - Global state management
- **React Query** - Server state management
- **SWR** - Data fetching and caching

### Form Handling
- **React Hook Form** - Form state management
- **Zod** - Schema validation
- **@hookform/resolvers** - Form validation integration

## 📱 Responsive Design

The frontend is built with a mobile-first approach:

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: > 1024px

### Breakpoints
```css
/* Tailwind CSS breakpoints */
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

## 🔐 Authentication Flow

1. **Login/Register**: Users authenticate via secure forms
2. **JWT Tokens**: Access and refresh tokens for session management
3. **Role-based Access**: Different features based on user role
4. **Protected Routes**: Authentication guards for sensitive pages
5. **Auto-refresh**: Seamless token renewal

## 🎯 Detection Modes

### Traditional Mode
- Fast processing with trained models
- Best for classic deepfakes
- Lower resource requirements

### Modern AI Mode
- Advanced generative AI integration
- GPT-4 Vision and Gemini Pro support
- Higher accuracy for modern synthetic content

### Hybrid Mode
- Combines all detection methods
- Maximum accuracy and coverage
- Most comprehensive analysis

## 📊 Real-time Features

### WebSocket Integration
- **Live Detection**: Real-time video analysis
- **Progress Updates**: Real-time processing status
- **Error Handling**: Graceful connection management
- **Reconnection**: Automatic reconnection on disconnect

### Performance Monitoring
- **Detection Metrics**: Processing time, accuracy scores
- **System Health**: Server status, model availability
- **User Analytics**: Usage patterns, feature adoption

## 🧪 Testing

### Running Tests
```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

### Test Structure
- **Unit Tests**: Component testing with React Testing Library
- **Integration Tests**: API integration testing
- **E2E Tests**: Full user flow testing

## 🚀 Deployment

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm run preview
```

### Environment-specific Builds
```bash
# Development build
npm run build:dev

# Production build
npm run build:prod
```

## 🔧 Development

### Code Style
- **ESLint**: Code linting and formatting
- **Prettier**: Code formatting
- **TypeScript**: Type safety and IntelliSense

### Component Guidelines
- **Functional Components**: Use React hooks
- **TypeScript**: Strict typing for all components
- **Props Interface**: Define clear prop interfaces
- **Error Boundaries**: Handle component errors gracefully

### State Management
- **Local State**: useState, useReducer for component state
- **Global State**: Context API for app-wide state
- **Server State**: React Query for API data

## 📚 API Documentation

### Key Endpoints
- `POST /api/detect-deepfake-upload-mode` - File upload detection
- `POST /api/detect-deepfake-youtube` - YouTube URL detection
- `WebSocket /ws/detect` - Real-time detection streaming
- `GET /api/startup/status` - System status

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/refresh` - Token refresh

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**"API connection failed"**
- Verify backend server is running on port 8000
- Check VITE_API_URL in .env.local
- Ensure CORS is properly configured

**"Authentication failed"**
- Check JWT token validity
- Verify SECRET_KEY in backend config
- Clear localStorage and re-login

**Build errors**
```bash
# Check TypeScript errors
npm run lint

# Clear Vite cache
rm -rf .vite
npm run dev
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Install dependencies: `npm install`
4. Make changes and test
5. Submit pull request

### Code Standards
- Follow TypeScript best practices
- Use meaningful component and variable names
- Add proper error handling
- Include JSDoc comments for complex functions

## 📄 License

This project is part of the Deepfake Detection System and is licensed under the MIT License.
