// Neo Alexandria 2.0 Frontend - Classification Page
// Browse and navigate classification hierarchy

import React from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { FolderTree } from 'lucide-react';

const ClassificationPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <FolderTree className="w-6 h-6 text-accent-blue-500" />
            <h1 className="text-2xl font-bold">Classification Browser</h1>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-charcoal-grey-400">
            Classification browser coming soon...
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export { ClassificationPage };
