/**
 * ErrorBoundary - React error boundary for catastrophic errors
 */
import { Component, type ReactNode } from 'react';
import { AlertTriangle } from 'lucide-react';
import { classifyError, formatErrorForLogging } from '@/lib/errors';

export interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    // Log error
    const classified = classifyError(error);
    console.error('[ErrorBoundary]', formatErrorForLogging(classified), errorInfo);

    // Call custom error handler
    this.props.onError?.(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-background p-4">
          <div className="max-w-md w-full">
            <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg p-6">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <AlertTriangle className="h-6 w-6 text-red-600 dark:text-red-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <h2 className="text-lg font-semibold text-red-900 dark:text-red-100 mb-2">
                    Something went wrong
                  </h2>
                  <p className="text-sm text-red-800 dark:text-red-200 mb-4">
                    The application encountered an unexpected error. Please try refreshing the page.
                  </p>
                  {import.meta.env.DEV && this.state.error && (
                    <details className="mb-4">
                      <summary className="text-sm font-medium text-red-900 dark:text-red-100 cursor-pointer mb-2">
                        Error details
                      </summary>
                      <pre className="text-xs bg-red-100 dark:bg-red-900 p-3 rounded overflow-auto max-h-48">
                        {this.state.error.message}
                        {'\n\n'}
                        {this.state.error.stack}
                      </pre>
                    </details>
                  )}
                  <div className="flex gap-2">
                    <button
                      onClick={this.handleReset}
                      className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md text-sm font-medium transition-colors"
                    >
                      Try again
                    </button>
                    <button
                      onClick={() => window.location.reload()}
                      className="px-4 py-2 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-red-900 dark:text-red-100 border border-red-200 dark:border-red-800 rounded-md text-sm font-medium transition-colors"
                    >
                      Reload page
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
