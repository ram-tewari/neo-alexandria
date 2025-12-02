/**
 * FeatureErrorBoundary Component
 * 
 * Error boundary for wrapping major features to prevent entire app crashes.
 * Displays user-friendly error UI with retry functionality.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Button } from '../ui/Button/Button';
import { Card } from '../ui/Card/Card';

interface Props {
  children: ReactNode;
  /** Optional fallback UI to display on error */
  fallback?: ReactNode;
  /** Optional callback when error occurs */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  /** Feature name for better error context */
  featureName?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Error boundary component that catches React errors in child components
 */
export class FeatureErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error details to console for debugging
    console.error('Error caught by FeatureErrorBoundary:', {
      featureName: this.props.featureName,
      error,
      errorInfo,
      componentStack: errorInfo.componentStack,
    });

    // Update state with error info
    this.setState({
      errorInfo,
    });

    // Call optional error callback
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleRetry = (): void => {
    // Reset error state to retry rendering
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
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
        <div className="error-boundary-container" style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '400px',
          padding: '2rem',
        }}>
          <Card style={{
            maxWidth: '600px',
            width: '100%',
            padding: '2rem',
            textAlign: 'center',
          }}>
            <div style={{
              fontSize: '3rem',
              marginBottom: '1rem',
            }}>
              ⚠️
            </div>
            
            <h2 style={{
              fontSize: '1.5rem',
              fontWeight: 600,
              marginBottom: '0.5rem',
              color: 'var(--color-text-primary)',
            }}>
              {this.props.featureName 
                ? `${this.props.featureName} Error` 
                : 'Something went wrong'}
            </h2>
            
            <p style={{
              color: 'var(--color-text-secondary)',
              marginBottom: '1.5rem',
            }}>
              We encountered an error while loading this feature. 
              You can try reloading or return to the previous page.
            </p>

            {/* Show error message in development */}
            {import.meta.env.DEV && this.state.error && (
              <details style={{
                marginBottom: '1.5rem',
                textAlign: 'left',
                padding: '1rem',
                backgroundColor: 'var(--color-background-secondary)',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
              }}>
                <summary style={{
                  cursor: 'pointer',
                  fontWeight: 600,
                  marginBottom: '0.5rem',
                  color: 'var(--color-error)',
                }}>
                  Error Details (Development Only)
                </summary>
                <pre style={{
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  fontSize: '0.75rem',
                  color: 'var(--color-text-secondary)',
                }}>
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}

            <div style={{
              display: 'flex',
              gap: '0.75rem',
              justifyContent: 'center',
            }}>
              <Button
                variant="primary"
                onClick={this.handleRetry}
              >
                Try Again
              </Button>
              <Button
                variant="secondary"
                onClick={() => window.history.back()}
              >
                Go Back
              </Button>
            </div>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

export default FeatureErrorBoundary;
