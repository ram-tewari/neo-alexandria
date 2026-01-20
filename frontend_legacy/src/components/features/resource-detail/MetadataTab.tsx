import { ResourceRead } from '../../../lib/api/types';
import './MetadataTab.css';

interface MetadataTabProps {
  resource: ResourceRead;
}

/**
 * MetadataTab - Displays all resource metadata
 * 
 * Shows Dublin Core fields and Neo Alexandria specific metadata
 * Organized into logical sections for better readability
 */
export const MetadataTab: React.FC<MetadataTabProps> = ({ resource }) => {
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  const formatReadStatus = (status?: string) => {
    if (!status) return undefined;
    return status.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const formatIngestionStatus = (status: string) => {
    const statusMap: Record<string, string> = {
      'pending': 'Pending',
      'processing': 'Processing',
      'completed': 'Completed',
      'failed': 'Failed'
    };
    return statusMap[status] || status;
  };

  // Dublin Core Metadata fields
  const dublinCoreFields = [
    { label: 'Title', value: resource.title },
    { label: 'Creator', value: resource.creator },
    { label: 'Publisher', value: resource.publisher },
    { label: 'Contributor', value: resource.contributor },
    { label: 'Date', value: resource.date },
    { label: 'Type', value: resource.type },
    { label: 'Format', value: resource.format },
    { label: 'Identifier', value: resource.identifier },
    { label: 'Source', value: resource.source },
    { label: 'Language', value: resource.language },
    { label: 'Relation', value: resource.relation },
    { label: 'Coverage', value: resource.coverage },
    { label: 'Rights', value: resource.rights },
  ];

  // Neo Alexandria specific fields
  const systemFields = [
    { label: 'Classification Code', value: resource.classification_code },
    { label: 'Quality Score', value: resource.quality_score ? `${(resource.quality_score * 100).toFixed(1)}%` : undefined },
    { label: 'Read Status', value: formatReadStatus(resource.read_status) },
    { label: 'Embedding Model', value: resource.embedding_model },
    { label: 'Has Embedding', value: resource.has_embedding ? 'Yes' : 'No' },
  ];

  // Ingestion status fields
  const ingestionFields = [
    { label: 'Ingestion Status', value: formatIngestionStatus(resource.ingestion_status) },
    { label: 'Ingestion Error', value: resource.ingestion_error },
    { label: 'Date Ingested', value: formatDate(resource.date_ingested) },
  ];

  // Timestamp fields
  const timestampFields = [
    { label: 'Date Created', value: formatDate(resource.date_created) },
    { label: 'Date Modified', value: formatDate(resource.date_modified) },
  ];

  const renderSection = (title: string, fields: Array<{ label: string; value?: string }>) => {
    const visibleFields = fields.filter(field => field.value);
    if (visibleFields.length === 0) return null;

    return (
      <div className="metadata-section">
        <h3 className="metadata-section-title">{title}</h3>
        <div className="metadata-grid">
          {visibleFields.map((field) => (
            <div key={field.label} className="metadata-field">
              <dt className="metadata-label">{field.label}</dt>
              <dd className="metadata-value">{field.value}</dd>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div
      role="tabpanel"
      id="panel-metadata"
      aria-labelledby="tab-metadata"
      className="metadata-tab"
    >
      {/* Subject Tags - Prominent display */}
      {resource.subject && resource.subject.length > 0 && (
        <div className="metadata-section">
          <h3 className="metadata-section-title">Subject</h3>
          <div className="subject-tags">
            {resource.subject.map((tag, index) => (
              <span key={`${tag}-${index}`} className="subject-tag">
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Description - Full width */}
      {resource.description && (
        <div className="metadata-section">
          <h3 className="metadata-section-title">Description</h3>
          <p className="metadata-description">{resource.description}</p>
        </div>
      )}

      {/* URL - Full width with link */}
      {resource.url && (
        <div className="metadata-section">
          <h3 className="metadata-section-title">URL</h3>
          <a
            href={resource.url}
            target="_blank"
            rel="noopener noreferrer"
            className="metadata-link"
          >
            {resource.url}
          </a>
        </div>
      )}

      {/* Dublin Core Metadata */}
      {renderSection('Dublin Core Metadata', dublinCoreFields)}

      {/* Neo Alexandria System Fields */}
      {renderSection('System Information', systemFields)}

      {/* Ingestion Status */}
      {renderSection('Ingestion Status', ingestionFields)}

      {/* Timestamps */}
      {renderSection('Timestamps', timestampFields)}
    </div>
  );
};
