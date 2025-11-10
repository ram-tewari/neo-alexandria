// Neo Alexandria 2.0 Frontend - Dropdown Component
// Dropdown menu using Headless UI with animations and keyboard navigation

import React, { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/utils/cn';

interface DropdownItem {
  label: string;
  onClick: () => void;
  icon?: React.ReactNode;
  disabled?: boolean;
  danger?: boolean;
}

interface DropdownProps {
  trigger: React.ReactNode;
  items: DropdownItem[];
  align?: 'left' | 'right';
  className?: string;
  menuClassName?: string;
}

const Dropdown: React.FC<DropdownProps> = ({
  trigger,
  items,
  align = 'right',
  className,
  menuClassName,
}) => {
  const alignClasses = {
    left: 'left-0 origin-top-left',
    right: 'right-0 origin-top-right',
  };

  return (
    <Menu as="div" className={cn('relative inline-block text-left', className)}>
      <Menu.Button as={Fragment}>
        {trigger}
      </Menu.Button>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-150"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-100"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items
          className={cn(
            'absolute z-50 mt-2 min-w-[12rem] rounded-lg',
            'bg-charcoal-grey-800 border border-charcoal-grey-700',
            'shadow-lg ring-1 ring-black ring-opacity-5',
            'focus:outline-none',
            'py-1',
            alignClasses[align],
            menuClassName
          )}
        >
          {items.map((item, index) => (
            <Menu.Item key={index} disabled={item.disabled}>
              {({ active }) => (
                <button
                  onClick={item.onClick}
                  disabled={item.disabled}
                  className={cn(
                    'w-full flex items-center px-4 py-2 text-sm',
                    'transition-colors duration-150',
                    active && !item.disabled && 'bg-charcoal-grey-700',
                    item.disabled && 'opacity-50 cursor-not-allowed',
                    item.danger
                      ? 'text-error hover:text-red-400'
                      : 'text-charcoal-grey-200 hover:text-charcoal-grey-50'
                  )}
                >
                  {item.icon && (
                    <span className="mr-3 flex-shrink-0">
                      {item.icon}
                    </span>
                  )}
                  <span>{item.label}</span>
                </button>
              )}
            </Menu.Item>
          ))}
        </Menu.Items>
      </Transition>
    </Menu>
  );
};

// Simple dropdown button component
interface DropdownButtonProps {
  children: React.ReactNode;
  className?: string;
}

const DropdownButton: React.FC<DropdownButtonProps> = ({ children, className }) => {
  return (
    <button
      aria-haspopup="true"
      className={cn(
        'inline-flex items-center justify-center gap-2',
        'px-4 py-2 text-sm font-medium',
        'text-charcoal-grey-200 bg-charcoal-grey-800',
        'border border-charcoal-grey-700 rounded-lg',
        'hover:bg-charcoal-grey-700 hover:text-charcoal-grey-50',
        'focus:outline-none focus:ring-2 focus:ring-accent-blue-500',
        'transition-colors duration-150',
        className
      )}
    >
      {children}
      <ChevronDown className="w-4 h-4" aria-hidden="true" />
    </button>
  );
};

export { Dropdown, DropdownButton };
export type { DropdownProps, DropdownItem, DropdownButtonProps };
