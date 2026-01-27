/**
 * Type Guards and Validators for Graph Types
 * 
 * Runtime type checking and validation utilities for graph domain models.
 * These functions provide type safety at runtime and help catch invalid data
 * from API responses or user input.
 */

import {
  HypothesisType,
  VisualizationMode,
} from './graph';

import type {
  GraphNode,
  GraphEdge,
  GraphData,
  Hypothesis,
  ABCHypothesis,
  GraphEntity,
  GraphRelationship,
  EntityType,
  RelationType,
  LayoutAlgorithm,
  ImpactLevel,
} from './graph';

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Type guard to check if a value is a valid HypothesisType
 */
export function isHypothesisType(value: unknown): value is HypothesisType {
  return (
    typeof value === 'string' &&
    Object.values(HypothesisType).includes(value as HypothesisType)
  );
}

/**
 * Type guard to check if a value is a valid VisualizationMode
 */
export function isVisualizationMode(value: unknown): value is VisualizationMode {
  return (
    typeof value === 'string' &&
    Object.values(VisualizationMode).includes(value as VisualizationMode)
  );
}

/**
 * Type guard to check if a value is a valid EntityType
 */
export function isEntityType(value: unknown): value is EntityType {
  const validTypes: EntityType[] = [
    'Concept',
    'Person',
    'Organization',
    'Method',
    'File',
    'Function',
    'Class',
    'Variable',
  ];
  return typeof value === 'string' && validTypes.includes(value as EntityType);
}

/**
 * Type guard to check if a value is a valid RelationType
 */
export function isRelationType(value: unknown): value is RelationType {
  const validTypes: RelationType[] = [
    'CONTRADICTS',
    'SUPPORTS',
    'EXTENDS',
    'CITES',
    'CALLS',
    'IMPORTS',
    'DEFINES',
    'SEMANTIC_SIMILARITY',
  ];
  return typeof value === 'string' && validTypes.includes(value as RelationType);
}

/**
 * Type guard to check if a value is a valid LayoutAlgorithm
 */
export function isLayoutAlgorithm(value: unknown): value is LayoutAlgorithm {
  const validAlgorithms: LayoutAlgorithm[] = [
    'force-directed',
    'hierarchical',
    'circular',
    'dagre',
    'manual',
  ];
  return typeof value === 'string' && validAlgorithms.includes(value as LayoutAlgorithm);
}

/**
 * Type guard to check if a value is a valid ImpactLevel
 */
export function isImpactLevel(value: unknown): value is ImpactLevel {
  return value === 'high' || value === 'medium' || value === 'low';
}

/**
 * Type guard to check if an object is a valid GraphNode
 */
export function isGraphNode(value: unknown): value is GraphNode {
  if (typeof value !== 'object' || value === null) return false;
  
  const node = value as Record<string, unknown>;
  
  return (
    typeof node.id === 'string' &&
    typeof node.label === 'string' &&
    typeof node.type === 'string' &&
    typeof node.metadata === 'object' &&
    node.metadata !== null &&
    typeof node.position === 'object' &&
    node.position !== null &&
    typeof (node.position as Record<string, unknown>).x === 'number' &&
    typeof (node.position as Record<string, unknown>).y === 'number'
  );
}

/**
 * Type guard to check if an object is a valid GraphEdge
 */
export function isGraphEdge(value: unknown): value is GraphEdge {
  if (typeof value !== 'object' || value === null) return false;
  
  const edge = value as Record<string, unknown>;
  
  return (
    typeof edge.id === 'string' &&
    typeof edge.source === 'string' &&
    typeof edge.target === 'string' &&
    typeof edge.type === 'string' &&
    typeof edge.weight === 'number' &&
    typeof edge.metadata === 'object' &&
    edge.metadata !== null
  );
}

/**
 * Type guard to check if an object is a valid GraphData
 */
export function isGraphData(value: unknown): value is GraphData {
  if (typeof value !== 'object' || value === null) return false;
  
  const data = value as Record<string, unknown>;
  
  return (
    Array.isArray(data.nodes) &&
    Array.isArray(data.edges) &&
    typeof data.metadata === 'object' &&
    data.metadata !== null
  );
}

/**
 * Type guard to check if an object is a valid Hypothesis
 */
export function isHypothesis(value: unknown): value is Hypothesis {
  if (typeof value !== 'object' || value === null) return false;
  
  const hyp = value as Record<string, unknown>;
  
  return (
    typeof hyp.id === 'string' &&
    isHypothesisType(hyp.type) &&
    typeof hyp.confidence === 'number' &&
    typeof hyp.evidence === 'object' &&
    hyp.evidence !== null &&
    Array.isArray(hyp.nodes)
  );
}

/**
 * Type guard to check if an object is a valid ABCHypothesis
 */
export function isABCHypothesis(value: unknown): value is ABCHypothesis {
  if (!isHypothesis(value)) return false;
  
  const hyp = value as Record<string, unknown>;
  
  return (
    hyp.type === HypothesisType.HIDDEN_CONNECTION &&
    typeof hyp.conceptA === 'string' &&
    typeof hyp.conceptC === 'string' &&
    typeof hyp.bridgingConcept === 'string' &&
    Array.isArray(hyp.aToB) &&
    Array.isArray(hyp.bToC)
  );
}

/**
 * Type guard to check if an object is a valid GraphEntity
 */
export function isGraphEntity(value: unknown): value is GraphEntity {
  if (typeof value !== 'object' || value === null) return false;
  
  const entity = value as Record<string, unknown>;
  
  return (
    typeof entity.id === 'string' &&
    typeof entity.name === 'string' &&
    isEntityType(entity.type) &&
    typeof entity.properties === 'object' &&
    entity.properties !== null
  );
}

/**
 * Type guard to check if an object is a valid GraphRelationship
 */
export function isGraphRelationship(value: unknown): value is GraphRelationship {
  if (typeof value !== 'object' || value === null) return false;
  
  const rel = value as Record<string, unknown>;
  
  return (
    typeof rel.id === 'string' &&
    typeof rel.source === 'string' &&
    typeof rel.target === 'string' &&
    isRelationType(rel.type) &&
    typeof rel.properties === 'object' &&
    rel.properties !== null
  );
}

// ============================================================================
// Validators
// ============================================================================

/**
 * Validation result type
 */
export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

/**
 * Validate a confidence score (0.0 - 1.0)
 */
export function validateConfidence(confidence: number): ValidationResult {
  const errors: string[] = [];
  
  if (typeof confidence !== 'number') {
    errors.push('Confidence must be a number');
  } else if (confidence < 0 || confidence > 1) {
    errors.push('Confidence must be between 0.0 and 1.0');
  } else if (isNaN(confidence)) {
    errors.push('Confidence cannot be NaN');
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Validate a weight value (0.0 - 1.0)
 */
export function validateWeight(weight: number): ValidationResult {
  const errors: string[] = [];
  
  if (typeof weight !== 'number') {
    errors.push('Weight must be a number');
  } else if (weight < 0 || weight > 1) {
    errors.push('Weight must be between 0.0 and 1.0');
  } else if (isNaN(weight)) {
    errors.push('Weight cannot be NaN');
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Validate a GraphNode
 */
export function validateGraphNode(node: unknown): ValidationResult {
  const errors: string[] = [];
  
  if (!isGraphNode(node)) {
    errors.push('Invalid GraphNode structure');
    return { valid: false, errors };
  }
  
  if (node.id.trim() === '') {
    errors.push('Node ID cannot be empty');
  }
  
  if (node.label.trim() === '') {
    errors.push('Node label cannot be empty');
  }
  
  const validTypes = ['default', 'cluster', 'entity', 'hypothesis'];
  if (!validTypes.includes(node.type)) {
    errors.push(`Invalid node type: ${node.type}`);
  }
  
  if (isNaN(node.position.x) || isNaN(node.position.y)) {
    errors.push('Node position coordinates must be valid numbers');
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Validate a GraphEdge
 */
export function validateGraphEdge(edge: unknown): ValidationResult {
  const errors: string[] = [];
  
  if (!isGraphEdge(edge)) {
    errors.push('Invalid GraphEdge structure');
    return { valid: false, errors };
  }
  
  if (edge.id.trim() === '') {
    errors.push('Edge ID cannot be empty');
  }
  
  if (edge.source.trim() === '') {
    errors.push('Edge source cannot be empty');
  }
  
  if (edge.target.trim() === '') {
    errors.push('Edge target cannot be empty');
  }
  
  if (edge.source === edge.target) {
    errors.push('Edge source and target cannot be the same (self-loops not allowed)');
  }
  
  const validTypes = ['default', 'citation', 'dependency', 'relationship', 'similarity'];
  if (!validTypes.includes(edge.type)) {
    errors.push(`Invalid edge type: ${edge.type}`);
  }
  
  const weightValidation = validateWeight(edge.weight);
  if (!weightValidation.valid) {
    errors.push(...weightValidation.errors);
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Validate a Hypothesis
 */
export function validateHypothesis(hypothesis: unknown): ValidationResult {
  const errors: string[] = [];
  
  if (!isHypothesis(hypothesis)) {
    errors.push('Invalid Hypothesis structure');
    return { valid: false, errors };
  }
  
  if (hypothesis.id.trim() === '') {
    errors.push('Hypothesis ID cannot be empty');
  }
  
  const confidenceValidation = validateConfidence(hypothesis.confidence);
  if (!confidenceValidation.valid) {
    errors.push(...confidenceValidation.errors);
  }
  
  if (hypothesis.nodes.length === 0) {
    errors.push('Hypothesis must involve at least one node');
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Validate a GraphEntity
 */
export function validateGraphEntity(entity: unknown): ValidationResult {
  const errors: string[] = [];
  
  if (!isGraphEntity(entity)) {
    errors.push('Invalid GraphEntity structure');
    return { valid: false, errors };
  }
  
  if (entity.id.trim() === '') {
    errors.push('Entity ID cannot be empty');
  }
  
  if (entity.name.trim() === '') {
    errors.push('Entity name cannot be empty');
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Validate a GraphRelationship
 */
export function validateGraphRelationship(relationship: unknown): ValidationResult {
  const errors: string[] = [];
  
  if (!isGraphRelationship(relationship)) {
    errors.push('Invalid GraphRelationship structure');
    return { valid: false, errors };
  }
  
  if (relationship.id.trim() === '') {
    errors.push('Relationship ID cannot be empty');
  }
  
  if (relationship.source.trim() === '') {
    errors.push('Relationship source cannot be empty');
  }
  
  if (relationship.target.trim() === '') {
    errors.push('Relationship target cannot be empty');
  }
  
  if (relationship.source === relationship.target) {
    errors.push('Relationship source and target cannot be the same');
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}
