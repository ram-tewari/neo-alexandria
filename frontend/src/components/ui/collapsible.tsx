import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface CollapsibleContextValue {
  open: boolean;
  setOpen: (open: boolean) => void;
  disabled?: boolean;
}

const CollapsibleContext = React.createContext<CollapsibleContextValue | undefined>(undefined);

function useCollapsible() {
  const context = React.useContext(CollapsibleContext);
  if (!context) {
    throw new Error('useCollapsible must be used within a Collapsible');
  }
  return context;
}

interface CollapsibleProps extends React.HTMLAttributes<HTMLDivElement> {
  open?: boolean;
  defaultOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  disabled?: boolean;
}

export function Collapsible({
  open: controlledOpen,
  defaultOpen = false,
  onOpenChange,
  disabled = false,
  children,
  className,
  ...props
}: CollapsibleProps) {
  const [internalOpen, setInternalOpen] = React.useState(defaultOpen);
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;

  const setOpen = React.useCallback(
    (newOpen: boolean) => {
      if (disabled) return;
      if (controlledOpen === undefined) {
        setInternalOpen(newOpen);
      }
      onOpenChange?.(newOpen);
    },
    [controlledOpen, disabled, onOpenChange]
  );

  const contextValue = React.useMemo(
    () => ({ open, setOpen, disabled }),
    [open, setOpen, disabled]
  );

  return (
    <CollapsibleContext.Provider value={contextValue}>
      <div className={className} data-state={open ? 'open' : 'closed'} {...props}>
        {children}
      </div>
    </CollapsibleContext.Provider>
  );
}

interface CollapsibleTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
}

export const CollapsibleTrigger = React.forwardRef<HTMLButtonElement, CollapsibleTriggerProps>(
  ({ asChild = false, onClick, children, ...props }, ref) => {
    const { open, setOpen, disabled } = useCollapsible();

    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
      if (!disabled) {
        setOpen(!open);
        onClick?.(e);
      }
    };

    if (asChild && React.isValidElement(children)) {
      return React.cloneElement(children as React.ReactElement<any>, {
        onClick: handleClick,
        'data-state': open ? 'open' : 'closed',
        'aria-expanded': open,
        ...props,
      });
    }

    return (
      <button
        ref={ref}
        type="button"
        data-state={open ? 'open' : 'closed'}
        aria-expanded={open}
        disabled={disabled}
        onClick={handleClick}
        {...props}
      >
        {children}
      </button>
    );
  }
);
CollapsibleTrigger.displayName = 'CollapsibleTrigger';

interface CollapsibleContentProps extends React.HTMLAttributes<HTMLDivElement> {
  forceMount?: boolean;
}

export const CollapsibleContent = React.forwardRef<HTMLDivElement, CollapsibleContentProps>(
  ({ forceMount = false, children, className, ...props }, ref) => {
    const { open } = useCollapsible();

    if (!forceMount && !open) {
      return null;
    }

    return (
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            ref={ref}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
            className={className}
            data-state={open ? 'open' : 'closed'}
            style={{ overflow: 'hidden' }}
            {...props}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    );
  }
);
CollapsibleContent.displayName = 'CollapsibleContent';
