# Frontend Architecture & Development Guide

## 🏗️ Architecture Overview

The Healthcare Voice AI frontend is built with React, TypeScript, and a comprehensive design system focused on accessibility and maintainability.

### Tech Stack
- **React 18** with TypeScript
- **React Router** for navigation
- **Design System** with accessible components
- **CSS Modules** for styling
- **Jest & React Testing Library** for testing

## 📁 Project Structure

```
frontend/
├── public/                     # Static assets
├── src/
│   ├── common/                 # Shared components & utilities
│   │   ├── components/
│   │   │   └── DesignSystem/   # Accessible UI components
│   │   ├── contexts/           # React contexts
│   │   ├── hooks/              # Custom hooks
│   │   ├── types/              # TypeScript definitions
│   │   └── utils/              # Utility functions
│   ├── features/               # Feature-based modules
│   │   ├── auth/               # Authentication
│   │   ├── dashboard/          # Dashboard
│   │   └── landing/            # Landing page
│   ├── layouts/                # Layout components
│   └── styles/                 # Global styles & design tokens
└── build/                      # Production build
```

## 🎨 Design System

### Core Components

#### Button
- **Variants**: `primary`, `secondary`, `outline`, `danger`, `ghost`
- **Sizes**: `sm`, `md`, `lg`
- **Features**: Loading states, icons, full-width, ARIA support
- **Accessibility**: Keyboard navigation, screen reader support

```tsx
<Button 
  variant="primary" 
  size="lg" 
  loading={isLoading}
  aria-label="Submit form"
>
  Submit
</Button>
```

#### Form Components
- **Input**: Text, email, password, etc. with validation
- **Textarea**: Multi-line text input
- **Select**: Dropdown selection
- **FormGroup**: Form field wrapper

```tsx
<FormGroup>
  <Input
    label="Email"
    type="email"
    required
    error={errors.email}
    helpText="We'll never share your email"
    onChange={setEmail}
  />
</FormGroup>
```

#### Card
- **Variants**: `default`, `elevated`, `outlined`
- **Padding**: `none`, `small`, `medium`, `large`

```tsx
<Card variant="elevated" padding="large">
  <h3>Card Title</h3>
  <p>Card content goes here</p>
</Card>
```

## 🎯 Accessibility Features

### ARIA Compliance
- All interactive elements have proper ARIA labels
- Form fields are properly associated with labels
- Error messages use `role="alert"`
- Loading states announce to screen readers

### Keyboard Navigation
- All interactive elements are keyboard accessible
- Focus management for modals and dropdowns
- Skip links for main content

### Color & Contrast
- WCAG AA compliant color combinations
- High contrast mode support
- Color is not the only indicator of state

### Screen Reader Support
- Semantic HTML structure
- Descriptive alt text for images
- Live regions for dynamic content

## 🧪 Testing Strategy

### Unit Tests
- Component behavior testing
- Hook testing
- Utility function testing

### Integration Tests
- User flow testing
- API integration testing
- Form submission testing

### Accessibility Tests
- Automated a11y testing with jest-axe
- Manual keyboard navigation testing
- Screen reader testing

## 🚀 Development Workflow

### Getting Started
```bash
cd frontend
npm install
npm start
```

### Available Scripts
- `npm start` - Development server
- `npm test` - Run tests
- `npm run build` - Production build
- `npm run lint` - ESLint checking
- `npm run type-check` - TypeScript checking

### Code Quality
- **ESLint** for code linting
- **Prettier** for code formatting
- **TypeScript** for type safety
- **Husky** for pre-commit hooks

## 📝 Component Guidelines

### Creating New Components
1. Use TypeScript interfaces for props
2. Include accessibility attributes
3. Add comprehensive tests
4. Follow naming conventions
5. Document with JSDoc

### Styling Guidelines
- Use CSS modules for component styles
- Follow BEM methodology
- Use design tokens for consistency
- Ensure responsive design

### State Management
- Use React hooks for local state
- Context API for global state
- Custom hooks for shared logic

## 🔧 Custom Hooks

### useApi
Centralized API call management with loading states and error handling.

```tsx
const { data, loading, error, execute } = useApi(apiCall, {
  immediate: true,
  cache: true,
  cacheKey: 'user-data'
});
```

### useForm
Form state management with validation.

```tsx
const { values, errors, handleChange, handleSubmit } = useForm({
  initialValues: { email: '', password: '' },
  validation: validationSchema
});
```

## 🎨 Design Tokens

Design tokens are defined in `styles/design-tokens.css`:

- **Colors**: Primary, secondary, semantic colors
- **Typography**: Font families, sizes, weights
- **Spacing**: Consistent spacing scale
- **Breakpoints**: Responsive design breakpoints
- **Shadows**: Elevation system
- **Border Radius**: Consistent corner rounding

## 📱 Responsive Design

- Mobile-first approach
- Breakpoints: `sm` (640px), `md` (768px), `lg` (1024px), `xl` (1280px)
- Flexible grid system
- Touch-friendly interface elements

## 🔒 Security Considerations

- Input sanitization
- XSS prevention
- CSRF protection
- Secure authentication flow
- Content Security Policy headers

## 🚀 Performance Optimization

- Code splitting with React.lazy
- Image optimization
- Bundle analysis
- Lazy loading for non-critical components
- Memoization for expensive operations

## 📊 Monitoring & Analytics

- Error boundary implementation
- Performance monitoring
- User interaction tracking
- Accessibility metrics

## 🤝 Contributing

### Code Style
- Follow existing patterns
- Write meaningful commit messages
- Add tests for new features
- Update documentation

### Pull Request Process
1. Create feature branch
2. Write tests
3. Update documentation
4. Submit PR with description
5. Address review feedback

## 📚 Resources

- [React Documentation](https://reactjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro)
- [Design System Best Practices](https://designsystemsrepo.com/)