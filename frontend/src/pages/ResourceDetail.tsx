// Neo Alexandria 2.0 Frontend - Resource Detail Page
// Detailed resource view with editing and curation capabilities

import React from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useResource } from '@/hooks/useApi';
import { BookOpen, Edit, ExternalLink, Share, Trash2 } from 'lucide-react';

interface ResourceDetailProps {
  edit?: boolean;
}

const ResourceDetail: React.FC<ResourceDetailProps> = ({ edit = false }) => {
  const { id } = useParams<{ id: string }>();
  const { data: resource, isLoading, error } = useResource(id!);

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="p-8">
            <LoadingSpinner centered text="Loading resource..." />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !resource) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="text-center py-12">
            <BookOpen className="w-16 h-16 mx-auto mb-4 text-secondary-400" />
            <h2 className="text-xl font-semibold mb-2">Resource Not Found</h2>
            <p className="text-secondary-600">The requested resource could not be found.</p>
            <Button 
              variant="outline" 
              onClick={() => window.history.back()}
              className="mt-4"
            >
              Go Back
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">
            {resource.title}
          </h1>
          <div className="flex items-center space-x-4 text-sm text-secondary-600">
            <span>{resource.creator}</span>
            <span>{resource.publisher}</span>
            <span>{new Date(resource.created_at).toLocaleDateString()}</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-2 ml-4">
          <Button variant="outline" size="sm" icon={<Edit className="w-4 h-4" />}>
            Edit
          </Button>
          <Button variant="outline" size="sm" icon={<Share className="w-4 h-4" />}>
            Share
          </Button>
          <Button variant="outline" size="sm" icon={<ExternalLink className="w-4 h-4" />}>
            Open Link
          </Button>
        </div>
      </div>

      {/* Content */}
      <Card>
        <CardContent className="p-6">
          <div className="prose max-w-none">
            {edit ? (
              <div className="space-y-4">
                <p className="text-secondary-600">Edit mode coming soon...</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2 mb-4">
                  {resource.subject.map((subject) => (
                    <Badge key={subject} variant="outline">
                      {subject}
                    </Badge>
                  ))}
                </div>
                
                {resource.description && (
                  <div>
                    <h3 className="text-lg font-medium mb-2">Description</h3>
                    <p className="text-secondary-700">{resource.description}</p>
                  </div>
                )}

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
                  <div>
                    <span className="text-sm text-secondary-600">Quality Score</span>
                    <div className="text-lg font-medium">{Math.round(resource.quality_score * 100)}%</div>
                  </div>
                  <div>
                    <span className="text-sm text-secondary-600">Read Status</span>
                    <div className="text-lg font-medium capitalize">{resource.read_status.replace('_', ' ')}</div>
                  </div>
                  <div>
                    <span className="text-sm text-secondary-600">Language</span>
                    <div className="text-lg font-medium">{resource.language || 'N/A'}</div>
                  </div>
                  <div>
                    <span className="text-sm text-secondary-600">Type</span>
                    <div className="text-lg font-medium">{resource.type || 'N/A'}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Coming Soon Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardContent className="p-6 text-center">
            <h3 className="text-lg font-medium mb-2">Knowledge Graph</h3>
            <p className="text-secondary-600 mb-4">View connections to related resources</p>
            <Button variant="outline" disabled>Coming Soon</Button>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6 text-center">
            <h3 className="text-lg font-medium mb-2">Quality Analysis</h3>
            <p className="text-secondary-600 mb-4">Detailed quality metrics and suggestions</p>
            <Button variant="outline" disabled>Coming Soon</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export { ResourceDetail };
