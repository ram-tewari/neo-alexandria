// Neo Alexandria 2.0 Frontend - Collections Page
// View and manage collections

import React from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { FolderOpen } from 'lucide-react';

const CollectionsPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <FolderOpen className="w-6 h-6 text-accent-blue-500" />
            <h1 className="text-2xl font-bold">Collections</h1>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-charcoal-grey-400">
            Collections management coming soon...
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export { CollectionsPage };
