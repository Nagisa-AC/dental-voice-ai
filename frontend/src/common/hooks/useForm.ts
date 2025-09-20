/**
 * Custom Hook for Form Handling
 * 
 * Provides form state management, validation, and submission handling.
 */

import { useState, useCallback, useRef, useEffect } from 'react';

interface FormField {
  value: any;
  error: string | null;
  touched: boolean;
}

interface FormState {
  [key: string]: FormField;
}

interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => string | null;
}

interface FormValidation {
  [key: string]: ValidationRule;
}

interface UseFormOptions<T> {
  initialValues: T;
  validation?: FormValidation;
  onSubmit: (values: T) => void | Promise<void>;
}

interface UseFormReturn<T> {
  values: T;
  errors: { [K in keyof T]: string | null };
  touched: { [K in keyof T]: boolean };
  isSubmitting: boolean;
  isValid: boolean;
  setValue: (field: keyof T, value: any) => void;
  setError: (field: keyof T, error: string | null) => void;
  setTouched: (field: keyof T, touched: boolean) => void;
  handleChange: (field: keyof T) => (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  handleBlur: (field: keyof T) => () => void;
  handleSubmit: (event: React.FormEvent) => Promise<void>;
  reset: () => void;
  validate: () => boolean;
  validateField: (field: keyof T) => boolean;
}

export function useForm<T extends Record<string, any>>({
  initialValues,
  validation = {},
  onSubmit,
}: UseFormOptions<T>): UseFormReturn<T> {
  const [formState, setFormState] = useState<FormState>(() => {
    const state: FormState = {};
    Object.keys(initialValues).forEach(key => {
      state[key] = {
        value: initialValues[key],
        error: null,
        touched: false,
      };
    });
    return state;
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const isSubmittingRef = useRef(false);

  // Validate a single field
  const validateField = useCallback((field: keyof T): boolean => {
    const fieldValue = formState[field as string]?.value;
    const rules = validation[field as string];
    
    if (!rules) return true;

    let error: string | null = null;

    // Required validation
    if (rules.required && (!fieldValue || fieldValue.toString().trim() === '')) {
      error = `${String(field)} is required`;
    }
    // Min length validation
    else if (rules.minLength && fieldValue && fieldValue.toString().length < rules.minLength) {
      error = `${String(field)} must be at least ${rules.minLength} characters`;
    }
    // Max length validation
    else if (rules.maxLength && fieldValue && fieldValue.toString().length > rules.maxLength) {
      error = `${String(field)} must be no more than ${rules.maxLength} characters`;
    }
    // Pattern validation
    else if (rules.pattern && fieldValue && !rules.pattern.test(fieldValue.toString())) {
      error = `${String(field)} format is invalid`;
    }
    // Custom validation
    else if (rules.custom) {
      error = rules.custom(fieldValue);
    }

    setFormState(prev => ({
      ...prev,
      [field]: {
        ...prev[field as string],
        error,
      },
    }));

    return !error;
  }, [formState, validation]);

  // Validate all fields
  const validate = useCallback((): boolean => {
    let isValid = true;
    Object.keys(validation).forEach(field => {
      if (!validateField(field as keyof T)) {
        isValid = false;
      }
    });
    return isValid;
  }, [validation, validateField]);

  // Set field value
  const setValue = useCallback((field: keyof T, value: any) => {
    setFormState(prev => ({
      ...prev,
      [field]: {
        ...prev[field as string],
        value,
        error: null, // Clear error when value changes
      },
    }));
  }, []);

  // Set field error
  const setError = useCallback((field: keyof T, error: string | null) => {
    setFormState(prev => ({
      ...prev,
      [field]: {
        ...prev[field as string],
        error,
      },
    }));
  }, []);

  // Set field touched state
  const setTouched = useCallback((field: keyof T, touched: boolean) => {
    setFormState(prev => ({
      ...prev,
      [field]: {
        ...prev[field as string],
        touched,
      },
    }));
  }, []);

  // Handle input change
  const handleChange = useCallback((field: keyof T) => (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const value = event.target.type === 'checkbox' 
      ? (event.target as HTMLInputElement).checked 
      : event.target.value;
    
    setValue(field, value);
  }, [setValue]);

  // Handle input blur
  const handleBlur = useCallback((field: keyof T) => () => {
    setTouched(field, true);
    validateField(field);
  }, [setTouched, validateField]);

  // Handle form submission
  const handleSubmit = useCallback(async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (isSubmittingRef.current) return;
    
    // Mark all fields as touched
    setFormState(prev => {
      const newState = { ...prev };
      Object.keys(newState).forEach(key => {
        newState[key] = { ...newState[key], touched: true };
      });
      return newState;
    });

    // Validate form
    if (!validate()) {
      return;
    }

    setIsSubmitting(true);
    isSubmittingRef.current = true;

    try {
      // Extract values from form state
      const values = Object.keys(formState).reduce((acc, key) => {
        acc[key as keyof T] = formState[key].value;
        return acc;
      }, {} as T);

      await onSubmit(values);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
      isSubmittingRef.current = false;
    }
  }, [formState, validate, onSubmit]);

  // Reset form
  const reset = useCallback(() => {
    setFormState(() => {
      const state: FormState = {};
      Object.keys(initialValues).forEach(key => {
        state[key] = {
          value: initialValues[key],
          error: null,
          touched: false,
        };
      });
      return state;
    });
    setIsSubmitting(false);
    isSubmittingRef.current = false;
  }, [initialValues]);

  // Extract values, errors, and touched states
  const values = Object.keys(formState).reduce((acc, key) => {
    acc[key as keyof T] = formState[key].value;
    return acc;
  }, {} as T);

  const errors = Object.keys(formState).reduce((acc, key) => {
    acc[key as keyof T] = formState[key].error;
    return acc;
  }, {} as { [K in keyof T]: string | null });

  const touched = Object.keys(formState).reduce((acc, key) => {
    acc[key as keyof T] = formState[key].touched;
    return acc;
  }, {} as { [K in keyof T]: boolean });

  // Check if form is valid
  const isValid = Object.values(errors).every(error => !error);

  return {
    values,
    errors,
    touched,
    isSubmitting,
    isValid,
    setValue,
    setError,
    setTouched,
    handleChange,
    handleBlur,
    handleSubmit,
    reset,
    validate,
    validateField,
  };
}
