import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../common/contexts/AuthContext';
import { Button, Card, FormGroup, Input } from '../../common';
import './Login.css';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <Card className="login-card" padding="large">
        <div className="login-header">
          <h1>🏥 Healthcare Voice AI</h1>
          <p>Sign in to your dashboard</p>
        </div>

        {error && (
          <div className="error-message" role="alert" aria-live="polite">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <FormGroup>
            <Input
              type="email"
              label="Email"
              value={email}
              onChange={setEmail}
              required
              autoComplete="email"
              autoFocus
              aria-describedby={error ? "error-message" : undefined}
            />
          </FormGroup>
          
          <FormGroup>
            <Input
              type="password"
              label="Password"
              value={password}
              onChange={setPassword}
              required
              autoComplete="current-password"
              aria-describedby={error ? "error-message" : undefined}
            />
          </FormGroup>
          
          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            loading={isLoading}
            loadingText="Signing In..."
            disabled={isLoading}
          >
            Sign In
          </Button>
        </form>

        <div className="demo-info">
          <p>Demo credentials: admin@healthcarevoice.ai / admin123</p>
        </div>
      </Card>
    </div>
  );
};

export default Login;