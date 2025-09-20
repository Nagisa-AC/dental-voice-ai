import React from 'react';
import './Card.css';

interface CardProps {
  variant?: 'default' | 'feature' | 'pricing' | 'testimonial';
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  featured?: boolean;
}

const Card: React.FC<CardProps> = ({
  variant = 'default',
  children,
  className = '',
  hover = true,
  featured = false,
}) => {
  const baseClasses = 'card-base';
  const variantClasses = {
    default: 'card-default',
    feature: 'card-feature',
    pricing: 'card-pricing',
    testimonial: 'card-testimonial',
  };

  const classes = [
    baseClasses,
    variantClasses[variant],
    hover ? 'card-hover' : '',
    featured ? 'card-featured' : '',
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={classes}>
      {children}
    </div>
  );
};

export default Card;
