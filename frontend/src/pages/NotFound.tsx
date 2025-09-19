// Neo Alexandria 2.0 Frontend - 404 Not Found Page
// Error page for unmatched routes

import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { BookOpen, Home, Search, ArrowLeft } from 'lucide-react';

const NotFound: React.FC = () => {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <Card className="max-w-lg w-full">
        <CardContent className="text-center p-8">
          <div className="text-secondary-400 mb-6">
            <BookOpen className="w-24 h-24 mx-auto mb-4" />
            <h1 className="text-4xl font-bold text-secondary-900 mb-2">404</h1>
            <h2 className="text-xl font-medium text-secondary-700 mb-2">
              Page Not Found
            </h2>
            <p className="text-secondary-600">
              The page you're looking for doesn't exist in your knowledge library.
            </p>
          </div>

          <div className="space-y-3">
            <Link to="/">
              <Button
                variant="primary"
                fullWidth
                icon={<Home className="w-4 h-4" />}
              >
                Go to Library
              </Button>
            </Link>
            
            <Link to="/search">
              <Button
                variant="outline"
                fullWidth
                icon={<Search className="w-4 h-4" />}
              >
                Search Resources
              </Button>
            </Link>
            
            <Button
              variant="ghost"
              fullWidth
              onClick={() => window.history.back()}
              icon={<ArrowLeft className="w-4 h-4" />}
            >
              Go Back
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export { NotFound };
