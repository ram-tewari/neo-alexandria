// Neo Alexandria 2.0 Frontend - Collection Detail Page
// View and manage a specific collection

import React from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { FolderOpen } from 'lucide-react';

const CollectionDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="container mx-auto px-4 py-8">
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <FolderOpen className="w-6 h-6 text-accent-blue-500" />
            <h1 className="text-2xl font-bold">Collection Details</h1>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-charcoal-grey-400">
            Collection {id} details coming soon...
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export { CollectionDetailPage };
