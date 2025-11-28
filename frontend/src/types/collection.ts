export interface Collection {
  id: string;
  name: string;
  description: string;
  type: 'manual' | 'smart';
  parentId?: string;
  thumbnail?: string;
  resourceIds: string[];
  resourceCount: number;
  rules?: CollectionRule[];
  sharing: 'private' | 'shared' | 'public';
  statistics: CollectionStatistics;
  createdAt: Date;
  updatedAt: Date;
}

export interface CollectionRule {
  id: string;
  field: 'quality' | 'classification' | 'author' | 'date' | 'tag';
  operator: '>' | '<' | '=' | 'contains' | 'in';
  value: any;
  logic: 'AND' | 'OR';
}

export interface CollectionStatistics {
  totalResources: number;
  averageQuality: number;
  topClassifications: { name: string; count: number }[];
  recentActivity: Date;
}

export interface CollectionTemplate {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  defaultRules?: CollectionRule[];
}
