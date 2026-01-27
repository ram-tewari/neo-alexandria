// Simple toast hook for notifications
export interface ToastProps {
  title: string;
  description?: string;
  variant?: 'default' | 'destructive';
}

export function useToast() {
  const toast = ({ title, description, variant = 'default' }: ToastProps) => {
    // Simple console log for now - can be enhanced with a toast library later
    console.log(`[Toast ${variant}]`, title, description);
    
    // You can integrate with a toast library like sonner or react-hot-toast here
    // For now, we'll just use browser notifications
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, { body: description });
    }
  };

  return { toast };
}
