import React from 'react';

export default function Input({
  label,
  id,
  type = 'text',
  value,
  onChange,
  placeholder = '',
  required = false,
  error = '',
  className = '',
  ...props
}) {
  return (
    <div className={`flex flex-col gap-2 text-left w-full ${className}`}>
      {label && (
        <label htmlFor={id} className="text-xs font-medium text-text-secondary tracking-wide">
          {label} {required && <span className="text-error">*</span>}
        </label>
      )}
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className={`w-full px-4 py-2.5 bg-background border ${
          error ? 'border-error focus:ring-error/20 focus:border-error' : 'border-border focus:ring-primary/20 focus:border-border-hover'
        } rounded-input text-text-primary placeholder:text-text-muted text-sm focus:outline-none focus:ring-4 transition-all duration-200`}
        {...props}
      />
      {error && <span className="text-xs text-error font-medium">{error}</span>}
    </div>
  );
}
