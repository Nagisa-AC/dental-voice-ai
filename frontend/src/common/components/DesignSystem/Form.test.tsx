import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { FormGroup, Input, Textarea, Select } from './Form';

describe('FormGroup Component', () => {
  test('renders children correctly', () => {
    render(
      <FormGroup>
        <input data-testid="child-input" />
      </FormGroup>
    );
    
    expect(screen.getByTestId('child-input')).toBeInTheDocument();
    expect(screen.getByTestId('child-input').parentElement).toHaveClass('form-group');
  });

  test('applies custom className', () => {
    render(
      <FormGroup className="custom-class">
        <input />
      </FormGroup>
    );
    
    expect(screen.getByRole('textbox').parentElement).toHaveClass('form-group', 'custom-class');
  });
});

describe('Input Component', () => {
  test('renders with label', () => {
    render(<Input label="Email" />);
    
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
  });

  test('renders with required indicator', () => {
    render(<Input label="Email" required />);
    
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  test('handles value changes', () => {
    const handleChange = jest.fn();
    render(<Input label="Email" onChange={handleChange} />);
    
    const input = screen.getByLabelText('Email');
    fireEvent.change(input, { target: { value: 'test@example.com' } });
    
    expect(handleChange).toHaveBeenCalledWith('test@example.com');
  });

  test('shows error message', () => {
    render(<Input label="Email" error="Invalid email" />);
    
    expect(screen.getByText('Invalid email')).toBeInTheDocument();
    expect(screen.getByText('Invalid email')).toHaveAttribute('role', 'alert');
    expect(screen.getByLabelText('Email')).toHaveClass('form-input-error');
  });

  test('shows help text when no error', () => {
    render(<Input label="Email" helpText="Enter your email address" />);
    
    expect(screen.getByText('Enter your email address')).toBeInTheDocument();
    expect(screen.getByText('Enter your email address')).toHaveAttribute('id', 'help-text');
  });

  test('prioritizes error over help text', () => {
    render(
      <Input 
        label="Email" 
        error="Invalid email" 
        helpText="Enter your email address" 
      />
    );
    
    expect(screen.getByText('Invalid email')).toBeInTheDocument();
    expect(screen.queryByText('Enter your email address')).not.toBeInTheDocument();
  });

  test('sets aria-describedby correctly', () => {
    render(<Input label="Email" helpText="Help text" />);
    
    const input = screen.getByLabelText('Email');
    expect(input).toHaveAttribute('aria-describedby', 'help-text');
  });

  test('sets aria-describedby for error', () => {
    render(<Input label="Email" error="Error message" />);
    
    const input = screen.getByLabelText('Email');
    expect(input).toHaveAttribute('aria-describedby', 'error-message');
  });

  test('applies custom className', () => {
    render(<Input label="Email" className="custom-class" />);
    
    expect(screen.getByLabelText('Email')).toHaveClass('form-input', 'custom-class');
  });

  test('forwards other props', () => {
    render(<Input label="Email" placeholder="Enter email" type="email" />);
    
    const input = screen.getByLabelText('Email');
    expect(input).toHaveAttribute('placeholder', 'Enter email');
    expect(input).toHaveAttribute('type', 'email');
  });
});

describe('Textarea Component', () => {
  test('renders textarea element', () => {
    render(<Textarea />);
    
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toHaveClass('form-textarea');
  });

  test('shows error message', () => {
    render(<Textarea error="Invalid input" />);
    
    expect(screen.getByText('Invalid input')).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toHaveClass('form-textarea-error');
  });

  test('applies custom className', () => {
    render(<Textarea className="custom-class" />);
    
    expect(screen.getByRole('textbox')).toHaveClass('form-textarea', 'custom-class');
  });
});

describe('Select Component', () => {
  const options = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3' },
  ];

  test('renders select with options', () => {
    render(<Select options={options} />);
    
    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();
    expect(select).toHaveClass('form-select');
    
    options.forEach(option => {
      expect(screen.getByText(option.label)).toBeInTheDocument();
    });
  });

  test('shows error message', () => {
    render(<Select options={options} error="Please select an option" />);
    
    expect(screen.getByText('Please select an option')).toBeInTheDocument();
    expect(screen.getByRole('combobox')).toHaveClass('form-select-error');
  });

  test('handles value changes', () => {
    const handleChange = jest.fn();
    render(<Select options={options} onChange={handleChange} />);
    
    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'option2' } });
    
    expect(handleChange).toHaveBeenCalled();
  });

  test('applies custom className', () => {
    render(<Select options={options} className="custom-class" />);
    
    expect(screen.getByRole('combobox')).toHaveClass('form-select', 'custom-class');
  });
});

