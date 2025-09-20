import React from 'react';
import './Form.css';

interface FormGroupProps {
  children: React.ReactNode;
  className?: string;
}

export const FormGroup: React.FC<FormGroupProps> = ({
  children,
  className = '',
}) => {
  return (
    <div className={`form-group ${className}`}>
      {children}
    </div>
  );
};

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helpText?: string;
  onChange?: (value: string) => void;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helpText,
  onChange,
  className = '',
  ...props
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(e.target.value);
    }
    // Also call the original onChange if provided
    if (props.onChange) {
      props.onChange(e);
    }
  };

  return (
    <div className="input-wrapper">
      {label && (
        <label className="form-label">
          {label}
          {props.required && <span className="required">*</span>}
        </label>
      )}
      <input
        className={`form-input ${error ? 'form-input-error' : ''} ${className}`}
        onChange={handleChange}
        aria-describedby={error ? "error-message" : helpText ? "help-text" : undefined}
        {...props}
      />
      {helpText && !error && <span id="help-text" className="form-help">{helpText}</span>}
      {error && <span id="error-message" className="form-error" role="alert">{error}</span>}
    </div>
  );
};

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string;
}

export const Textarea: React.FC<TextareaProps> = ({
  error,
  className = '',
  ...props
}) => {
  return (
    <div className="input-wrapper">
      <textarea
        className={`form-textarea ${error ? 'form-textarea-error' : ''} ${className}`}
        {...props}
      />
      {error && <span className="form-error">{error}</span>}
    </div>
  );
};

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: string;
  options: { value: string; label: string }[];
}

export const Select: React.FC<SelectProps> = ({
  error,
  options,
  className = '',
  ...props
}) => {
  return (
    <div className="input-wrapper">
      <select
        className={`form-select ${error ? 'form-select-error' : ''} ${className}`}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <span className="form-error">{error}</span>}
    </div>
  );
};
