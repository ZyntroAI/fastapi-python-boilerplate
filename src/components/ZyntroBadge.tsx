import React from 'react';

type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info' | 'neon';
type BadgeSize = 'sm' | 'md' | 'lg';

interface ZyntroBadgeProps {
  variant?: BadgeVariant;
  size?: BadgeSize;
  children: React.ReactNode;
  className?: string;
}

const variantStyles: Record<BadgeVariant, string> = {
  default: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100',
  success: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-100',
  warning: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-100',
  danger: 'bg-rose-100 text-rose-800 dark:bg-rose-900 dark:text-rose-100',
  info: 'bg-sky-100 text-sky-800 dark:bg-sky-900 dark:text-sky-100',
  neon: 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/30 dark:shadow-cyan-400/20'
};

const sizeStyles: Record<BadgeSize, string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-3 py-1 text-sm',
  lg: 'px-4 py-1.5 text-base'
};

export function ZyntroBadge({
  variant = 'default',
  size = 'md',
  children,
  className = ''
}: ZyntroBadgeProps) {
  return (
    <span
      className={`inline-flex items-center font-medium rounded-full transition-none ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
    >
      {children}
    </span>
  );
}
