/**
 * Gallery Area Component
 * 
 * Main content area showing collection resources with breadcrumbs and view toggle
 */

import { Icon } from '../common/Icon';
import { icons } from '@/config/icons';
import { ViewModeSelector } from '../common/ViewModeSelector';
import { GridView } from '../views/GridView';
import { ListView } from '../views/ListView';
import { HeadlinesView } from '../views/HeadlinesView';
import { MasonryView } from '../views/MasonryView';
import { useResourceStore, useCollectionStore } from '@/store';
import './GalleryArea.css';

interface GalleryAreaProps {
  onRead?: (id: string) => void;
  onArchive?: (id: string) => void;
  onAnnotate?: (id: string) => void;
  onShare?: (id: string) => void;
}

export const GalleryArea = ({ onRead, onArchive, onAnnotate, onShare }: GalleryAreaProps) => {
  const { viewMode, setViewMode } = useResourceStore();
  const { activeCollection } = useCollectionStore();

  const resources = activeCollection?.resources || [];

  const renderView = () => {
    const viewProps = {
      resources: resources as any,
      onRead,
      onArchive,
      onAnnotate,
      onShare,
    };

    switch (viewMode) {
      case 'list':
        return <ListView {...viewProps} />;
      case 'headlines':
        return <HeadlinesView {...viewProps} />;
      case 'masonry':
        return <MasonryView {...viewProps} />;
      case 'grid':
      default:
        return <GridView {...viewProps} />;
    }
  };

  return (
    <div className="gallery-area">
      <div className="gallery-area__header">
        <div className="gallery-area__breadcrumbs">
          <button className="breadcrumb-item">
            <Icon icon={icons.library} size={16} />
            <span>Collections</span>
          </button>
          {activeCollection && (
            <>
              <Icon icon={icons.chevronRight} size={14} />
              <span className="breadcrumb-item active">{activeCollection.name}</span>
            </>
          )}
        </div>

        <div className="gallery-area__actions">
          <ViewModeSelector currentMode={viewMode} onChange={setViewMode} />
          <button className="gallery-area__add-btn">
            <Icon icon={icons.add} size={18} />
            <span>Add Resource</span>
          </button>
        </div>
      </div>

      <div className="gallery-area__content">
        {resources.length === 0 ? (
          <div className="gallery-area__empty">
            <Icon icon={icons.library} size={48} />
            <h3>No resources in this collection</h3>
            <p>Add resources to get started</p>
          </div>
        ) : (
          renderView()
        )}
      </div>
    </div>
  );
};
