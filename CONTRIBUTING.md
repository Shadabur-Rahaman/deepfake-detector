# 🤝 Contributing to Deepfake Detection System

Thank you for your interest in contributing to the Deepfake Detection System! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

## 📜 Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to conduct@deepfake-detector.com.

### Our Pledge
- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites
- **Python 3.11+** (3.13 recommended)
- **Node.js 18+** (20+ recommended)
- **Git** for version control
- **Docker** (optional, for containerized development)

### Fork and Clone
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/deepfake-detector.git
cd deepfake-detector

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/deepfake-detector.git
```

## 🛠️ Development Setup

### Backend Setup
```bash
# Create virtual environment
python -m venv deepfake-env
source deepfake-env/bin/activate  # On Windows: deepfake-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Copy configuration
cp config.env.example config.env
# Edit config.env with your settings

# Start backend server
cd backend/app
python main.py
```

### Frontend Setup
```bash
# Install dependencies
cd frontend
npm install

# Create environment file
cp .env.example .env.local

# Start development server
npm run dev
```

### Docker Setup (Optional)
```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individual containers
docker build -t deepfake-detector .
docker run -p 8000:8000 deepfake-detector
```

## 📝 Contributing Guidelines

### Types of Contributions
- **Bug Fixes**: Fix existing issues
- **Feature Additions**: Add new functionality
- **Documentation**: Improve documentation
- **Performance**: Optimize existing code
- **Testing**: Add or improve tests
- **UI/UX**: Improve user interface and experience

### Before You Start
1. **Check existing issues**: Look for similar issues or feature requests
2. **Create an issue**: For major changes, create an issue first to discuss
3. **Fork the repository**: Create your own fork
4. **Create a branch**: Use descriptive branch names

### Branch Naming Convention
```bash
# Feature branches
feature/add-new-detection-mode
feature/improve-ui-performance

# Bug fix branches
fix/resolve-memory-leak
fix/correct-api-endpoint

# Documentation branches
docs/update-api-documentation
docs/add-contributing-guide

# Refactoring branches
refactor/optimize-model-loading
refactor/improve-error-handling
```

## 🔄 Pull Request Process

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Write clean, readable code
- Follow the code style guidelines
- Add tests for new functionality
- Update documentation as needed

### 3. Commit Changes
```bash
# Use conventional commit messages
git add .
git commit -m "feat: add new detection mode for modern AI tools"
git commit -m "fix: resolve memory leak in model loading"
git commit -m "docs: update API documentation"
```

### 4. Push and Create PR
```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

### Pull Request Template
When creating a PR, please include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 🎨 Code Style

### Python Code Style
- **Formatter**: Black (line length: 88)
- **Linter**: flake8
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Google style docstrings

```python
def detect_deepfake(image: np.ndarray, mode: str = "hybrid") -> Dict[str, Any]:
    """
    Detect deepfakes in an image using specified mode.
    
    Args:
        image: Input image as numpy array
        mode: Detection mode ('traditional', 'modern-ai', 'hybrid')
        
    Returns:
        Dictionary containing detection results
        
    Raises:
        ValueError: If mode is not supported
        RuntimeError: If model loading fails
    """
    pass
```

### TypeScript/JavaScript Code Style
- **Formatter**: Prettier
- **Linter**: ESLint
- **TypeScript**: Strict mode enabled
- **Naming**: camelCase for variables, PascalCase for components

```typescript
interface DetectionResult {
  result: 'authentic' | 'deepfake' | 'borderline';
  confidence: number;
  processingTime: number;
}

const DetectionComponent: React.FC<Props> = ({ onResult }) => {
  const [isLoading, setIsLoading] = useState(false);
  
  const handleDetection = async (file: File): Promise<void> => {
    // Implementation
  };
  
  return (
    <div className="detection-component">
      {/* JSX */}
    </div>
  );
};
```

### File Organization
```
backend/app/
├── services/           # Business logic
├── models/            # Data models
├── routes/            # API endpoints
├── auth/              # Authentication
├── utils/             # Utility functions
└── tests/             # Test files

frontend/src/
├── components/        # Reusable components
├── pages/            # Page components
├── hooks/            # Custom hooks
├── contexts/         # React contexts
├── lib/              # Utility libraries
└── types/            # TypeScript types
```

## 🧪 Testing

### Backend Testing
```bash
# Run all tests
pytest

# Run specific test categories
pytest backend/tests/test_detection.py
pytest backend/tests/test_authentication.py
pytest backend/tests/test_models.py

# Run with coverage
pytest --cov=backend/app --cov-report=html

# Run linting
flake8 backend/app
black --check backend/app
```

### Frontend Testing
```bash
cd frontend

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run linting
npm run lint

# Type checking
npm run type-check
```

### Test Requirements
- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test API endpoints and database interactions
- **E2E Tests**: Test complete user workflows
- **Performance Tests**: Test model loading and inference speed

### Writing Tests
```python
# Backend test example
import pytest
from backend.app.services.deepfake_detector import DeepfakeDetector

class TestDeepfakeDetector:
    def test_detect_image_traditional_mode(self):
        detector = DeepfakeDetector()
        result = detector.detect(image_path, mode="traditional")
        
        assert result["confidence"] >= 0.0
        assert result["confidence"] <= 100.0
        assert result["result"] in ["authentic", "deepfake", "borderline"]
```

```typescript
// Frontend test example
import { render, screen } from '@testing-library/react';
import { DetectionComponent } from './DetectionComponent';

describe('DetectionComponent', () => {
  it('renders upload button', () => {
    render(<DetectionComponent onResult={jest.fn()} />);
    expect(screen.getByText('Upload File')).toBeInTheDocument();
  });
  
  it('handles file upload', async () => {
    const mockOnResult = jest.fn();
    render(<DetectionComponent onResult={mockOnResult} />);
    
    // Test file upload functionality
  });
});
```

## 📚 Documentation

### Code Documentation
- **Docstrings**: All functions should have docstrings
- **Comments**: Complex logic should be commented
- **Type Hints**: Use type hints for better documentation
- **README Updates**: Update README for new features

### API Documentation
- **OpenAPI**: Keep API documentation up to date
- **Examples**: Provide usage examples
- **Error Codes**: Document all error codes and responses

### User Documentation
- **Setup Guide**: Keep installation instructions current
- **User Guide**: Document new features and workflows
- **Troubleshooting**: Add solutions for common issues

## 🐛 Issue Reporting

### Bug Reports
When reporting bugs, please include:

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Windows 11, Ubuntu 20.04]
- Python Version: [e.g., 3.13]
- Node.js Version: [e.g., 20.0]
- Browser: [e.g., Chrome 120]

**Additional Context**
Screenshots, logs, or other relevant information
```

### Feature Requests
For feature requests, please include:

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why this feature would be useful

**Proposed Solution**
How you envision this feature working

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Any other relevant information
```

## 🔧 Development Tools

### Recommended IDE Setup
- **VS Code** with extensions:
  - Python
  - TypeScript and JavaScript
  - ESLint
  - Prettier
  - GitLens
  - Thunder Client (for API testing)

### Git Hooks
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Hooks will run on commit:
# - Black formatting
# - flake8 linting
# - TypeScript checking
# - Test running
```

### Debugging
```bash
# Backend debugging
cd backend/app
python -m pdb main.py

# Frontend debugging
cd frontend
npm run dev -- --debug
```

## 🚀 Release Process

### Version Numbering
We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated
- [ ] Release notes prepared
- [ ] Tag created in Git

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For general questions and ideas
- **Email**: dev@deepfake-detector.com
- **Discord**: [Join our Discord server](https://discord.gg/deepfake-detector)

### Mentorship
- **New Contributors**: We welcome new contributors and provide mentorship
- **Code Reviews**: All PRs receive thorough code reviews
- **Documentation**: We help improve documentation and guides

## 🏆 Recognition

### Contributors
All contributors are recognized in:
- **CONTRIBUTORS.md**: List of all contributors
- **Release Notes**: Contributors mentioned in releases
- **GitHub**: Contributors shown in repository insights

### Types of Contributions
- **Code**: Bug fixes, features, optimizations
- **Documentation**: Guides, API docs, tutorials
- **Testing**: Test cases, bug reports, quality assurance
- **Community**: Helping others, answering questions

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You

Thank you for contributing to the Deepfake Detection System! Your contributions help make AI more transparent and trustworthy.

Every contribution, no matter how small, makes a difference. Whether you're fixing a typo, adding a feature, or improving documentation, you're helping build a better future for AI detection technology.

---

**Happy Coding! 🚀**
