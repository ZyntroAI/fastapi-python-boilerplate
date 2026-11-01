import React from 'react';

type CardVariant = 'default' | 'elevated' | 'outlined' | 'glass';

interface ZyntroCardProps {
  variant?: CardVariant;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

const variantStyles: Record<CardVariant, string> = {
  default: 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800',
  elevated: 'bg-white dark:bg-gray-900 shadow-lg dark:shadow-gray-950/50',
  outlined: 'bg-transparent border-2 border-gray-300 dark:border-gray-700',
  glass: 'bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border border-white/20 dark:border-gray-800/50'
};

export function ZyntroCard({
  variant = 'default',
  children,
  className = '',
  onClick
}: ZyntroCardProps) {
  return (
    <div
      onClick={onClick}
      className={`rounded-xl p-5 transition-none ${variantStyles[variant]} ${onClick ? 'cursor-pointer hover:scale-[1.01]' : ''} ${className}`}
    >
      {children}
    </div>
  );
}
