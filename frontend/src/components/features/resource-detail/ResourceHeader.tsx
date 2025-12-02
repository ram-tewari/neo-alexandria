import { ResourceRead } from '../../../lib/api/types';
import './ResourceHeader.css';

interface ResourceHeaderProps {
  resource: ResourceRead;
}

/**
 * ResourceHeader - Displays resource title, metadata, and tags
 * 
 * Shows:
 * - Title
 * - Creator/author
 * - Type
 * - Date
 * - Language
 * - Subject tags as pills
 */
export const ResourceHeader: React.FC<ResourceHeaderProps> = ({ resource }) => {
  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch {
      return dateString;
    }
  };

  return (
    <header className="resource-header">
      <h1 className="resource-title">{resource.title}</h1>

      <div className="resource-metadata">
        {resource.creator && (
          <div className="metadata-item">
            <svg
              className="metadata-icon"
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M8 8a3 3 0 100-6 3 3 0 000 6zM8 9.5c-2.67 0-8 1.34-8 4v1.5h16v-1.5c0-2.66-5.33-4-8-4z"
                fill="currentColor"
              />
            </svg>
            <span>{resource.creator}</span>
          </div>
        )}

        {resource.type && (
          <div className="metadata-item">
            <svg
              className="metadata-icon"
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M3 2h10a1 1 0 011 1v10a1 1 0 01-1 1H3a1 1 0 01-1-1V3a1 1 0 011-1zm1 2v8h8V4H4z"
                fill="currentColor"
              />
            </svg>
            <span>{resource.type}</span>
          </div>
        )}

        {resource.date && (
          <div className="metadata-item">
            <svg
              className="metadata-icon"
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M5 2V1h1v1h4V1h1v1h2a1 1 0 011 1v11a1 1 0 01-1 1H3a1 1 0 01-1-1V3a1 1 0 011-1h2zm8 3H3v8h10V5z"
                fill="currentColor"
              />
            </svg>
            <span>{formatDate(resource.date)}</span>
          </div>
        )}

        {resource.language && (
          <div className="metadata-item">
            <svg
              className="metadata-icon"
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M8 1a7 7 0 100 14A7 7 0 008 1zm0 1.5c.85 0 1.65.2 2.36.55A6.5 6.5 0 018 8.5a6.5 6.5 0 01-2.36-5.45A5.5 5.5 0 018 2.5zm-3.5 1.14A7.5 7.5 0 008 9.5a7.5 7.5 0 003.5-5.86A5.48 5.48 0 0113.5 8c0 3.03-2.47 5.5-5.5 5.5S2.5 11.03 2.5 8c0-1.52.62-2.9 1.62-3.9z"
                fill="currentColor"
              />
            </svg>
            <span>{resource.language}</span>
          </div>
        )}
      </div>

      {resource.subject && resource.subject.length > 0 && (
        <div className="resource-tags">
          {resource.subject.map((tag, index) => (
            <span key={`${tag}-${index}`} className="tag-pill">
              {tag}
            </span>
          ))}
        </div>
      )}
    </header>
  );
};
