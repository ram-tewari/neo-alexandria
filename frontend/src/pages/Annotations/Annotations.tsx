import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AnnotationNotebook } from '@/components/annotation/AnnotationNotebook';
import { Annotation } from '@/types/annotation';

export const Annotations: React.FC = () => {
  const navigate = useNavigate();

  const handleAnnotationClick = (annotation: Annotation) => {
    // Navigate to the resource with the annotation highlighted
    navigate(`/resources/${annotation.resourceId}?annotation=${annotation.id}`);
  };

  return (
    <div className="h-full">
      <AnnotationNotebook onAnnotationClick={handleAnnotationClick} />
    </div>
  );
};
