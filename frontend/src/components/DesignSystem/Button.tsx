import React, { forwardRef, useCallback, useRef, useEffect } from 'react';
import { KEYBOARD_KEYS, ScreenReader } from '../../utils/accessibility';
import './Button.css';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  loadingText?: string;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  ariaDescribedBy?: string;
  ariaExpanded?: boolean;
  ariaPressed?: boolean;
  ariaControls?: string;
  ariaLabel?: string;
  ariaLabelledBy?: string;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onKeyDown?: (event: React.KeyboardEvent<HTMLButtonElement>) => void;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      loadingText = 'Loading...',
      icon,
      iconPosition = 'left',
      fullWidth = false,
      children,
      className = '',
      disabled,
      ariaDescribedBy,
      ariaExpanded,
      ariaPressed,
      ariaControls,
      ariaLabel,
      ariaLabelledBy,
      onClick,
      onKeyDown,
      ...props
    },
    ref
  ) => {
    const buttonRef = useRef<HTMLButtonElement>(null);
    const combinedRef = ref || buttonRef;

    // Handle click events
    const handleClick = useCallback(
      (event: React.MouseEvent<HTMLButtonElement>) => {
        if (loading || disabled) {
          event.preventDefault();
          return;
        }
        onClick?.(event);
      },
      [loading, disabled, onClick]
    );

    // Handle keyboard events
    const handleKeyDown = useCallback(
      (event: React.KeyboardEvent<HTMLButtonElement>) => {
        // Handle Enter and Space keys for button activation
        if (event.key === KEYBOARD_KEYS.ENTER || event.key === KEYBOARD_KEYS.SPACE) {
          if (loading || disabled) {
            event.preventDefault();
            return;
          }
          
          // For Space key, prevent default scrolling behavior
          if (event.key === KEYBOARD_KEYS.SPACE) {
            event.preventDefault();
          }
          
          // Trigger click
          onClick?.(event as any);
        }
        
        onKeyDown?.(event);
      },
      [loading, disabled, onClick, onKeyDown]
    );

    // Announce loading state to screen readers
    useEffect(() => {
      if (loading) {
        ScreenReader.announce(loadingText, 'polite');
      }
    }, [loading, loadingText]);

    // Build CSS classes
    const baseClasses = 'btn-base';
    const variantClasses = {
      primary: 'btn-primary',
      secondary: 'btn-secondary',
      outline: 'btn-outline',
      danger: 'btn-danger',
      ghost: 'btn-ghost',
    };
    const sizeClasses = {
      sm: 'btn-sm',
      md: 'btn-md',
      lg: 'btn-lg',
    };

    const classes = [
      baseClasses,
      variantClasses[variant],
      sizeClasses[size],
      fullWidth && 'btn-full-width',
      loading && 'btn-loading',
      disabled && 'btn-disabled',
      className,
    ].filter(Boolean).join(' ');

    // Build ARIA attributes
    const ariaAttributes: React.AriaAttributes = {
      'aria-disabled': loading || disabled || undefined,
      'aria-busy': loading || undefined,
      'aria-describedby': ariaDescribedBy,
      'aria-expanded': ariaExpanded,
      'aria-pressed': ariaPressed,
      'aria-controls': ariaControls,
      'aria-label': ariaLabel,
      'aria-labelledby': ariaLabelledBy,
    };

    // Remove undefined values
    Object.keys(ariaAttributes).forEach(key => {
      if (ariaAttributes[key as keyof React.AriaAttributes] === undefined) {
        delete ariaAttributes[key as keyof React.AriaAttributes];
      }
    });

    return (
      <button
        ref={combinedRef}
        type="button"
        className={classes}
        disabled={loading || disabled}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        {...ariaAttributes}
        {...props}
      >
        {loading && (
          <span className="btn-loading" aria-hidden="true">
            <svg
              className="btn-spinner"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeDasharray="31.416"
                strokeDashoffset="31.416"
              >
                <animate
                  attributeName="stroke-dasharray"
                  dur="2s"
                  values="0 31.416;15.708 15.708;0 31.416"
                  repeatCount="indefinite"
                />
                <animate
                  attributeName="stroke-dashoffset"
                  dur="2s"
                  values="0;-15.708;-31.416"
                  repeatCount="indefinite"
                />
              </circle>
            </svg>
          </span>
        )}
        
        {icon && iconPosition === 'left' && (
          <span className="btn-icon btn-icon--left" aria-hidden="true">
            {icon}
          </span>
        )}
        
        <span className="btn-content">
          {children}
        </span>
        
        {icon && iconPosition === 'right' && (
          <span className="btn-icon btn-icon--right" aria-hidden="true">
            {icon}
          </span>
        )}
        
        {loading && (
          <span className="sr-only">{loadingText}</span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
