// Neo Alexandria 2.0 Frontend - Add Resource Page
// URL ingestion interface with real-time status tracking

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useUrlIngestion } from '@/hooks/useApi';
import { useProcessingResources, useAppStore } from '@/store';
import { 
  Plus, 
  Link as LinkIcon, 
  Globe, 
  Check, 
  X, 
  Clock, 
  AlertCircle,
  FileText,
  Sparkles,
  ArrowRight,
  BookOpen
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { formatRelativeTime, extractDomain } from '@/utils/format';
import type { ProcessingResource } from '@/types/api';

const AddResource: React.FC = () => {
  const navigate = useNavigate();
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');
  const [errors, setErrors] = useState<{ url?: string; title?: string }>({});
  
  const { ingestUrl, isLoading } = useUrlIngestion();
  const processingResources = useProcessingResources();
  const addNotification = useAppStore(state => state.addNotification);

  const validateUrl = (url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Reset errors
    setErrors({});
    
    // Validation
    const newErrors: { url?: string; title?: string } = {};
    
    if (!url.trim()) {
      newErrors.url = 'URL is required';
    } else if (!validateUrl(url)) {
      newErrors.url = 'Please enter a valid URL';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      await ingestUrl(url, title || undefined);
      
      // Clear form
      setUrl('');
      setTitle('');
      
      addNotification({
        type: 'success',
        title: 'Resource Added to Queue',
        message: 'Your resource is being processed. You can track progress below.',
      });
    } catch (error) {
      setErrors({ url: 'Failed to add resource. Please try again.' });
    }
  };

  const handleQuickAdd = (quickUrl: string) => {
    setUrl(quickUrl);
  };

  const quickAddSuggestions = [
    {
      url: 'https://example.com/machine-learning-basics',
      title: 'Machine Learning Basics',
      domain: 'example.com',
      type: 'article',
    },
    {
      url: 'https://example.com/python-tutorial',
      title: 'Python Programming Tutorial',
      domain: 'example.com',
      type: 'tutorial',
    },
    {
      url: 'https://example.com/ai-research-paper',
      title: 'Latest AI Research Paper',
      domain: 'example.com',
      type: 'paper',
    },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-secondary-900 mb-2">
          Add Resource to Library
        </h1>
        <p className="text-secondary-600">
          Enter a URL to automatically extract and process content with AI-powered analysis
        </p>
      </div>

      {/* Main Form */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Plus className="w-5 h-5 text-primary-600" />
            <h2 className="text-xl font-semibold">Add New Resource</h2>
          </div>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2">
                <Input
                  label="URL"
                  placeholder="https://example.com/article"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  error={errors.url}
                  leftIcon={<LinkIcon className="w-4 h-4" />}
                  disabled={isLoading}
                />
              </div>
              
              <div>
                <Input
                  label="Title (Optional)"
                  placeholder="Custom title..."
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  error={errors.title}
                  leftIcon={<FileText className="w-4 h-4" />}
                  disabled={isLoading}
                  hint="Leave empty to auto-extract"
                />
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center space-x-2 text-sm text-secondary-600">
                <Sparkles className="w-4 h-4" />
                <span>AI will automatically extract content, generate summary, and add tags</span>
              </div>
              
              <Button
                type="submit"
                variant="primary"
                loading={isLoading}
                disabled={!url.trim() || isLoading}
                icon={<Plus className="w-4 h-4" />}
              >
                Add Resource
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Quick Add Suggestions */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-medium">Quick Add Examples</h3>
          <p className="text-sm text-secondary-600">
            Try these example URLs to see the processing in action
          </p>
        </CardHeader>
        
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {quickAddSuggestions.map((suggestion, index) => (
              <div
                key={index}
                className="border border-secondary-200 rounded-lg p-3 hover:border-primary-300 transition-colors cursor-pointer"
                onClick={() => handleQuickAdd(suggestion.url)}
              >
                <div className="flex items-start justify-between mb-2">
                  <Badge variant="outline" size="sm">
                    {suggestion.type}
                  </Badge>
                  <Globe className="w-4 h-4 text-secondary-400" />
                </div>
                
                <h4 className="font-medium text-secondary-900 mb-1 line-clamp-2">
                  {suggestion.title}
                </h4>
                
                <p className="text-sm text-secondary-500 mb-2">
                  {suggestion.domain}
                </p>
                
                <div className="flex items-center text-primary-600 text-sm">
                  <span>Quick add</span>
                  <ArrowRight className="w-3 h-3 ml-1" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Processing Queue */}
      {processingResources.length > 0 && (
        <ProcessingQueue />
      )}

      {/* How it Works */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-medium">How It Works</h3>
        </CardHeader>
        
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              {
                icon: <LinkIcon className="w-6 h-6" />,
                title: 'Submit URL',
                description: 'Paste any web URL you want to save and analyze',
              },
              {
                icon: <Sparkles className="w-6 h-6" />,
                title: 'AI Processing',
                description: 'Content is extracted and analyzed with AI for summary and tags',
              },
              {
                icon: <BookOpen className="w-6 h-6" />,
                title: 'Auto Classification',
                description: 'Resources are automatically classified using subject taxonomy',
              },
              {
                icon: <Check className="w-6 h-6" />,
                title: 'Ready to Use',
                description: 'Search, browse, and discover connections in your library',
              },
            ].map((step, index) => (
              <div key={index} className="text-center">
                <div className="w-12 h-12 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center mx-auto mb-3">
                  {step.icon}
                </div>
                <h4 className="font-medium text-secondary-900 mb-2">{step.title}</h4>
                <p className="text-sm text-secondary-600">{step.description}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Processing Queue Component
const ProcessingQueue: React.FC = () => {
  const processingResources = useProcessingResources();
  const removeProcessingResource = useAppStore(state => state.removeProcessingResource);

  const activeResources = processingResources.filter(
    r => r.status === 'pending' || r.status === 'processing'
  );
  const completedResources = processingResources.filter(
    r => r.status === 'completed' || r.status === 'failed'
  );

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Clock className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-medium">Processing Queue</h3>
            {activeResources.length > 0 && (
              <Badge variant="info" size="sm">
                {activeResources.length} active
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-3">
          {/* Active Processing */}
          {activeResources.map((resource) => (
            <ProcessingResourceItem
              key={resource.id}
              resource={resource}
              onRemove={() => removeProcessingResource(resource.id)}
            />
          ))}

          {/* Completed Resources */}
          {completedResources.map((resource) => (
            <ProcessingResourceItem
              key={resource.id}
              resource={resource}
              onRemove={() => removeProcessingResource(resource.id)}
            />
          ))}

          {processingResources.length === 0 && (
            <div className="text-center py-6 text-secondary-500">
              <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No resources currently being processed</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Individual Processing Resource Item
interface ProcessingResourceItemProps {
  resource: ProcessingResource;
  onRemove: () => void;
}

const ProcessingResourceItem: React.FC<ProcessingResourceItemProps> = ({
  resource,
  onRemove,
}) => {
  const getStatusIcon = () => {
    switch (resource.status) {
      case 'pending':
      case 'processing':
        return <LoadingSpinner size="sm" />;
      case 'completed':
        return <Check className="w-4 h-4 text-green-600" />;
      case 'failed':
        return <X className="w-4 h-4 text-red-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = () => {
    switch (resource.status) {
      case 'pending':
      case 'processing':
        return 'border-blue-200 bg-blue-50';
      case 'completed':
        return 'border-green-200 bg-green-50';
      case 'failed':
        return 'border-red-200 bg-red-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <div className={cn('border rounded-lg p-3', getStatusColor())}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1 min-w-0">
          <div className="flex-shrink-0 mt-0.5">
            {getStatusIcon()}
          </div>
          
          <div className="flex-1 min-w-0">
            <p className="font-medium text-secondary-900 truncate">
              {resource.title}
            </p>
            <p className="text-sm text-secondary-600 truncate">
              {extractDomain(resource.url)}
            </p>
            <div className="flex items-center space-x-4 mt-1 text-xs text-secondary-500">
              <span>Started {formatRelativeTime(resource.startedAt.toISOString())}</span>
              <Badge
                variant={
                  resource.status === 'completed' ? 'success' :
                  resource.status === 'failed' ? 'error' : 'info'
                }
                size="sm"
              >
                {resource.status.replace('_', ' ')}
              </Badge>
            </div>
            
            {resource.error && (
              <div className="flex items-center space-x-1 mt-2 text-sm text-red-600">
                <AlertCircle className="w-4 h-4" />
                <span>{resource.error}</span>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2 ml-4">
          {resource.status === 'completed' && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => window.location.href = `/resource/${resource.id}`}
            >
              View
            </Button>
          )}
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onRemove}
            icon={<X className="w-3 h-3" />}
          />
        </div>
      </div>
    </div>
  );
};

export { AddResource };
