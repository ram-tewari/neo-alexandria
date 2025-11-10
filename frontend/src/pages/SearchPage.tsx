// Neo Alexandria 2.0 Frontend - Search Page
// Advanced search with hybrid search and faceted filtering

import React from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Search } from 'lucide-react';

const SearchPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Search className="w-6 h-6 text-accent-blue-500" />
            <h1 className="text-2xl font-bold">Search</h1>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-charcoal-grey-400">
            Advanced search functionality coming soon...
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export { SearchPage };
