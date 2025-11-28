export interface Resource {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  content?: string;
  type: 'pdf' | 'url' | 'arxiv';
  url?: string;
  filePath?: string;
  thumbnail?: string;
  qualityScore: number;
  qualityDimensions: QualityDimension[];
  classification: string[];
  tags: string[];
  metadata: ResourceMetadata;
  createdAt: Date;
  updatedAt: Date;
}

export interface ResourceMetadata {
  doi?: string;
  arxivId?: string;
  publicationDate?: Date;
  journal?: string;
  citationCount?: number;
  pageCount?: number;
  fileSize?: number;
}

export interface QualityDimension {
  name: string;
  score: number;
  maxScore: number;
  description: string;
}

export interface UploadProgress {
  id: string;
  filename: string;
  progress: number;
  stage: 'uploading' | 'extracting' | 'analyzing' | 'complete' | 'error';
  error?: string;
}

export interface UploadStatus {
  id: string;
  status: 'pending' | 'processing' | 'complete' | 'error';
  progress: number;
  stage: string;
  error?: string;
}

export type ViewMode = 'card' | 'list' | 'compact';
export type DensityMode = 'comfortable' | 'compact' | 'spacious';
export type SortOption = 'recent' | 'title' | 'quality' | 'relevance';

export interface ResourceFilters {
  type?: ('pdf' | 'url' | 'arxiv')[];
  qualityMin?: number;
  qualityMax?: number;
  classification?: string[];
  tags?: string[];
  dateRange?: [Date, Date];
  searchQuery?: string;
}
