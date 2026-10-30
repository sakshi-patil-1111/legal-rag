import React from 'react';

export default function Card({ children, className = '', hoverEffect = true, ...props }) {
  return (
    <div
      className={`bg-paper-warm rounded-card border border-paper-rule p-6 relative flex flex-col justify-between shadow-stamp ${
        hoverEffect ? 'hover:shadow-card hover:border-paper-border transition-all duration-200' : ''
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
