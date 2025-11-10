// Neo Alexandria 2.0 Frontend - Resource Header Component
// Displays resource metadata and action buttons

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { useUpdateResource, useDeleteResource } from '@/hooks/useResources';
import { useToast } from '@/hooks/useToast';
import type { Resource } from '@/types/api';
import {
  Edit,
  Trash2,
  FolderPlus,
  ExternalLink,
  Calendar,
  User,
  Building,
  Globe,
} from 'lucide-react';

interface ResourceHeaderProps {
  resource: Resource;
}

// Read status dropdown options
const READ_STATUS_OPTIONS = [
  { value: 'unread', label: 'Unread', color: 'bg-charcoal-grey-600' },
  { value: 'in_progress', label: 'In Progress', color: 'bg-accent-blue-500' },
  { value: 'completed', label: 'Completed', color: 'bg-green-500' },
  { value: 'archived', label: 'Archived', color: 'bg-neutral-blue-600' },
] as const;

export const ResourceHeader: React.FC<ResourceHeaderProps> = ({ resource }) => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const updateResource = useUpdateResource();
  const deleteResource = useDeleteResource();
  const [isDeleting, setIsDeleting] = useState(false);

  // Get quality score color
  const getQualityColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-400';
    if (score >= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  // Get quality score label
  const getQualityLabel = (score: number): string => {
    if (score >= 0.8) return 'High Quality';
    if (score >= 0.6) return 'Medium Quality';
    return 'Needs Review';
  };

  // Handle read status change
  const handleReadStatusChange = async (newStatus: Resource['read_status']) => {
    try {
      await updateResource.mutateAsync({
        id: resource.id,
        data: { read_status: newStatus },
      });
      showToast({
        type: 'success',
        message: 'Read status updated successfully',
      });
    } catch (error) {
      showToast({
        type: 'error',
        message: 'Failed to update read status',
      });
    }
  };

  // Handle delete
  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this resource? This action cannot be undone.')) {
      return;
    }

    setIsDeleting(true);
    try {
      await deleteResource.mutateAsync(resource.id);
      showToast({
        type: 'success',
        message: 'Resource deleted successfully',
      });
      navigate('/library');
    } catch (error) {
      showToast({
        type: 'error',
        message: 'Failed to delete resource',
      });
      setIsDeleting(false);
    }
  };

  // Handle external link
  const handleOpenExternal = () => {
    if (resource.source || resource.url) {
      window.open(resource.source || resource.url, '_blank', 'noopener,noreferrer');
    }
  };

  // Get current read status option
  const currentStatus = READ_STATUS_OPTIONS.find(opt => opt.value === resource.read_status);

  return (
    <Card className="bg-charcoal-grey-800 border-charcoal-grey-700">
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Title and Actions Row */}
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <h1 className="text-3xl font-bold text-charcoal-grey-50 mb-2 break-words">
                {resource.title}
              </h1>
              
              {/* Badges Row */}
              <div className="flex flex-wrap items-center gap-2 mb-3">
                {/* Classification Badge */}
                {resource.classification_code && (
                  <Badge variant="info" size="md">
                    {resource.classification_code}
                  </Badge>
                )}
                
                {/* Quality Score Badge */}
                <Badge 
                  variant="outline" 
                  size="md"
                  className={`${getQualityColor(resource.quality_score)} border-current`}
                >
                  {Math.round(resource.quality_score * 100)}% - {getQualityLabel(resource.quality_score)}
                </Badge>

                {/* Read Status Badge */}
                <div className="relative group">
                  <Badge 
                    variant="default" 
                    size="md"
                    className={`${currentStatus?.color} text-white cursor-pointer hover:opacity-80 transition-opacity`}
                  >
                    {currentStatus?.label}
                  </Badge>
                  
                  {/* Read Status Dropdown */}
                  <div className="absolute top-full left-0 mt-1 hidden group-hover:block z-10">
                    <div className="bg-charcoal-grey-700 border border-charcoal-grey-600 rounded-lg shadow-lg py-1 min-w-[140px]">
                      {READ_STATUS_OPTIONS.map((option) => (
                        <button
                          key={option.value}
                          onClick={() => handleReadStatusChange(option.value)}
                          className="w-full px-3 py-2 text-left text-sm text-charcoal-grey-50 hover:bg-charcoal-grey-600 transition-colors flex items-center gap-2"
                        >
                          <span className={`w-2 h-2 rounded-full ${option.color}`} />
                          {option.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2 flex-shrink-0">
              <Button
                variant="outline"
                size="sm"
                icon={<Edit />}
                onClick={() => navigate(`/resources/${resource.id}/edit`)}
              >
                Edit
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                icon={<FolderPlus />}
                onClick={() => {
                  // TODO: Implement add to collection modal
                  showToast({ type: 'info', message: 'Add to collection coming soon' });
                }}
              >
                Add to Collection
              </Button>

              {(resource.source || resource.url) && (
                <Button
                  variant="outline"
                  size="sm"
                  icon={<ExternalLink />}
                  onClick={handleOpenExternal}
                >
                  Open Source
                </Button>
              )}

              <Button
                variant="danger"
                size="sm"
                icon={<Trash2 />}
                onClick={handleDelete}
                loading={isDeleting}
              >
                Delete
              </Button>
            </div>
          </div>

          {/* Metadata Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t border-charcoal-grey-700">
            {/* Creator */}
            {resource.creator && (
              <div className="flex items-start gap-2">
                <User className="w-4 h-4 text-charcoal-grey-400 mt-0.5 flex-shrink-0" />
                <div className="min-w-0">
                  <div className="text-xs text-charcoal-grey-400 mb-0.5">Creator</div>
                  <div className="text-sm text-charcoal-grey-50 truncate" title={resource.creator}>
                    {resource.creator}
                  </div>
                </div>
              </div>
            )}

            {/* Publisher */}
            {resource.publisher && (
              <div className="flex items-start gap-2">
                <Building className="w-4 h-4 text-charcoal-grey-400 mt-0.5 flex-shrink-0" />
                <div className="min-w-0">
                  <div className="text-xs text-charcoal-grey-400 mb-0.5">Publisher</div>
                  <div className="text-sm text-charcoal-grey-50 truncate" title={resource.publisher}>
                    {resource.publisher}
                  </div>
                </div>
              </div>
            )}

            {/* Language */}
            {resource.language && (
              <div className="flex items-start gap-2">
                <Globe className="w-4 h-4 text-charcoal-grey-400 mt-0.5 flex-shrink-0" />
                <div className="min-w-0">
                  <div className="text-xs text-charcoal-grey-400 mb-0.5">Language</div>
                  <div className="text-sm text-charcoal-grey-50 truncate">
                    {resource.language}
                  </div>
                </div>
              </div>
            )}

            {/* Created Date */}
            <div className="flex items-start gap-2">
              <Calendar className="w-4 h-4 text-charcoal-grey-400 mt-0.5 flex-shrink-0" />
              <div className="min-w-0">
                <div className="text-xs text-charcoal-grey-400 mb-0.5">Added</div>
                <div className="text-sm text-charcoal-grey-50">
                  {new Date(resource.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Source URL */}
          {resource.source && (
            <div className="pt-3 border-t border-charcoal-grey-700">
              <div className="text-xs text-charcoal-grey-400 mb-1">Source</div>
              <a
                href={resource.source}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-accent-blue-400 hover:text-accent-blue-300 transition-colors break-all"
              >
                {resource.source}
              </a>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
