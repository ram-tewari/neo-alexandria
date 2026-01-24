/**
 * Monaco Editor theme configuration
 * 
 * Provides custom themes for light and dark modes that integrate
 * with the application's Tailwind theme system.
 * 
 * Features:
 * - Comprehensive syntax highlighting for all supported languages
 * - WCAG AA compliant color contrast
 * - Gutter decoration styling
 * - Smooth theme transitions
 */

import type * as Monaco from 'monaco-editor';

/**
 * Pharos Light Theme
 * 
 * A clean, professional light theme with excellent readability
 * and WCAG AA compliant contrast ratios.
 */
export const lightTheme: Monaco.editor.IStandaloneThemeData = {
  base: 'vs',
  inherit: true,
  rules: [
    // Comments
    { token: 'comment', foreground: '6a737d', fontStyle: 'italic' },
    { token: 'comment.line', foreground: '6a737d', fontStyle: 'italic' },
    { token: 'comment.block', foreground: '6a737d', fontStyle: 'italic' },
    { token: 'comment.doc', foreground: '6a737d', fontStyle: 'italic' },
    
    // Keywords
    { token: 'keyword', foreground: 'd73a49', fontStyle: 'bold' },
    { token: 'keyword.control', foreground: 'd73a49', fontStyle: 'bold' },
    { token: 'keyword.operator', foreground: 'd73a49' },
    { token: 'keyword.other', foreground: 'd73a49' },
    
    // Strings
    { token: 'string', foreground: '032f62' },
    { token: 'string.quoted', foreground: '032f62' },
    { token: 'string.template', foreground: '032f62' },
    { token: 'string.regexp', foreground: '22863a' },
    
    // Numbers
    { token: 'number', foreground: '005cc5' },
    { token: 'number.float', foreground: '005cc5' },
    { token: 'number.hex', foreground: '005cc5' },
    { token: 'number.octal', foreground: '005cc5' },
    { token: 'number.binary', foreground: '005cc5' },
    
    // Functions
    { token: 'function', foreground: '6f42c1' },
    { token: 'function.call', foreground: '6f42c1' },
    { token: 'function.definition', foreground: '6f42c1', fontStyle: 'bold' },
    { token: 'method', foreground: '6f42c1' },
    { token: 'method.call', foreground: '6f42c1' },
    
    // Classes and Types
    { token: 'class', foreground: '22863a', fontStyle: 'bold' },
    { token: 'class.name', foreground: '22863a', fontStyle: 'bold' },
    { token: 'type', foreground: '22863a' },
    { token: 'type.identifier', foreground: '22863a' },
    { token: 'interface', foreground: '22863a', fontStyle: 'bold' },
    { token: 'struct', foreground: '22863a', fontStyle: 'bold' },
    { token: 'enum', foreground: '22863a', fontStyle: 'bold' },
    
    // Variables
    { token: 'variable', foreground: 'e36209' },
    { token: 'variable.name', foreground: 'e36209' },
    { token: 'variable.parameter', foreground: 'e36209' },
    { token: 'variable.other', foreground: '24292e' },
    { token: 'identifier', foreground: '24292e' },
    
    // Constants
    { token: 'constant', foreground: '005cc5', fontStyle: 'bold' },
    { token: 'constant.numeric', foreground: '005cc5' },
    { token: 'constant.language', foreground: '005cc5', fontStyle: 'bold' },
    { token: 'constant.character', foreground: '005cc5' },
    
    // Operators
    { token: 'operator', foreground: 'd73a49' },
    { token: 'delimiter', foreground: '24292e' },
    { token: 'delimiter.bracket', foreground: '24292e' },
    { token: 'delimiter.parenthesis', foreground: '24292e' },
    
    // Tags (HTML/XML)
    { token: 'tag', foreground: '22863a' },
    { token: 'tag.id', foreground: '6f42c1' },
    { token: 'tag.class', foreground: '6f42c1' },
    { token: 'attribute.name', foreground: '6f42c1' },
    { token: 'attribute.value', foreground: '032f62' },
    
    // Annotations/Decorators
    { token: 'annotation', foreground: '6f42c1' },
    { token: 'decorator', foreground: '6f42c1' },
    { token: 'meta', foreground: '6f42c1' },
    
    // Special
    { token: 'invalid', foreground: 'cb2431', fontStyle: 'bold' },
    { token: 'error', foreground: 'cb2431', fontStyle: 'bold' },
    { token: 'warning', foreground: 'e36209' },
    { token: 'info', foreground: '005cc5' },
    
    // Markdown specific
    { token: 'emphasis', fontStyle: 'italic' },
    { token: 'strong', fontStyle: 'bold' },
    { token: 'header', foreground: '22863a', fontStyle: 'bold' },
    { token: 'link', foreground: '005cc5', fontStyle: 'underline' },
    
    // JSON specific
    { token: 'key', foreground: '6f42c1' },
    { token: 'property', foreground: '6f42c1' },
  ],
  colors: {
    // Editor background and foreground
    'editor.background': '#ffffff',
    'editor.foreground': '#24292e',
    
    // Line highlighting
    'editor.lineHighlightBackground': '#f6f8fa',
    'editor.lineHighlightBorder': '#e1e4e8',
    
    // Selection
    'editor.selectionBackground': '#c8e1ff',
    'editor.selectionHighlightBackground': '#e8f2ff',
    'editor.inactiveSelectionBackground': '#e8f2ff',
    
    // Line numbers
    'editorLineNumber.foreground': '#959da5',
    'editorLineNumber.activeForeground': '#24292e',
    
    // Gutter (where decorations appear)
    'editorGutter.background': '#ffffff',
    'editorGutter.modifiedBackground': '#e36209',
    'editorGutter.addedBackground': '#22863a',
    'editorGutter.deletedBackground': '#cb2431',
    
    // Cursor
    'editorCursor.foreground': '#24292e',
    'editorCursor.background': '#ffffff',
    
    // Whitespace
    'editorWhitespace.foreground': '#d1d5da',
    
    // Indentation guides
    'editorIndentGuide.background': '#e1e4e8',
    'editorIndentGuide.activeBackground': '#959da5',
    
    // Brackets
    'editorBracketMatch.background': '#c8e1ff',
    'editorBracketMatch.border': '#005cc5',
    
    // Find/Replace
    'editor.findMatchBackground': '#ffdf5d',
    'editor.findMatchHighlightBackground': '#ffdf5d80',
    'editor.findRangeHighlightBackground': '#ffdf5d40',
    
    // Scrollbar
    'scrollbarSlider.background': '#959da580',
    'scrollbarSlider.hoverBackground': '#959da5a0',
    'scrollbarSlider.activeBackground': '#959da5c0',
    
    // Widget (hover cards, suggestions)
    'editorWidget.background': '#f6f8fa',
    'editorWidget.border': '#e1e4e8',
    'editorWidget.foreground': '#24292e',
    'editorHoverWidget.background': '#ffffff',
    'editorHoverWidget.border': '#e1e4e8',
    
    // Suggest widget
    'editorSuggestWidget.background': '#ffffff',
    'editorSuggestWidget.border': '#e1e4e8',
    'editorSuggestWidget.foreground': '#24292e',
    'editorSuggestWidget.selectedBackground': '#f6f8fa',
    'editorSuggestWidget.highlightForeground': '#005cc5',
  },
};

/**
 * Pharos Dark Theme
 * 
 * A modern dark theme optimized for extended coding sessions
 * with reduced eye strain and WCAG AA compliant contrast.
 */
export const darkTheme: Monaco.editor.IStandaloneThemeData = {
  base: 'vs-dark',
  inherit: true,
  rules: [
    // Comments
    { token: 'comment', foreground: '8b949e', fontStyle: 'italic' },
    { token: 'comment.line', foreground: '8b949e', fontStyle: 'italic' },
    { token: 'comment.block', foreground: '8b949e', fontStyle: 'italic' },
    { token: 'comment.doc', foreground: '8b949e', fontStyle: 'italic' },
    
    // Keywords
    { token: 'keyword', foreground: 'ff7b72', fontStyle: 'bold' },
    { token: 'keyword.control', foreground: 'ff7b72', fontStyle: 'bold' },
    { token: 'keyword.operator', foreground: 'ff7b72' },
    { token: 'keyword.other', foreground: 'ff7b72' },
    
    // Strings
    { token: 'string', foreground: 'a5d6ff' },
    { token: 'string.quoted', foreground: 'a5d6ff' },
    { token: 'string.template', foreground: 'a5d6ff' },
    { token: 'string.regexp', foreground: '7ee787' },
    
    // Numbers
    { token: 'number', foreground: '79c0ff' },
    { token: 'number.float', foreground: '79c0ff' },
    { token: 'number.hex', foreground: '79c0ff' },
    { token: 'number.octal', foreground: '79c0ff' },
    { token: 'number.binary', foreground: '79c0ff' },
    
    // Functions
    { token: 'function', foreground: 'd2a8ff' },
    { token: 'function.call', foreground: 'd2a8ff' },
    { token: 'function.definition', foreground: 'd2a8ff', fontStyle: 'bold' },
    { token: 'method', foreground: 'd2a8ff' },
    { token: 'method.call', foreground: 'd2a8ff' },
    
    // Classes and Types
    { token: 'class', foreground: '7ee787', fontStyle: 'bold' },
    { token: 'class.name', foreground: '7ee787', fontStyle: 'bold' },
    { token: 'type', foreground: '7ee787' },
    { token: 'type.identifier', foreground: '7ee787' },
    { token: 'interface', foreground: '7ee787', fontStyle: 'bold' },
    { token: 'struct', foreground: '7ee787', fontStyle: 'bold' },
    { token: 'enum', foreground: '7ee787', fontStyle: 'bold' },
    
    // Variables
    { token: 'variable', foreground: 'ffa657' },
    { token: 'variable.name', foreground: 'ffa657' },
    { token: 'variable.parameter', foreground: 'ffa657' },
    { token: 'variable.other', foreground: 'c9d1d9' },
    { token: 'identifier', foreground: 'c9d1d9' },
    
    // Constants
    { token: 'constant', foreground: '79c0ff', fontStyle: 'bold' },
    { token: 'constant.numeric', foreground: '79c0ff' },
    { token: 'constant.language', foreground: '79c0ff', fontStyle: 'bold' },
    { token: 'constant.character', foreground: '79c0ff' },
    
    // Operators
    { token: 'operator', foreground: 'ff7b72' },
    { token: 'delimiter', foreground: 'c9d1d9' },
    { token: 'delimiter.bracket', foreground: 'c9d1d9' },
    { token: 'delimiter.parenthesis', foreground: 'c9d1d9' },
    
    // Tags (HTML/XML)
    { token: 'tag', foreground: '7ee787' },
    { token: 'tag.id', foreground: 'd2a8ff' },
    { token: 'tag.class', foreground: 'd2a8ff' },
    { token: 'attribute.name', foreground: 'd2a8ff' },
    { token: 'attribute.value', foreground: 'a5d6ff' },
    
    // Annotations/Decorators
    { token: 'annotation', foreground: 'd2a8ff' },
    { token: 'decorator', foreground: 'd2a8ff' },
    { token: 'meta', foreground: 'd2a8ff' },
    
    // Special
    { token: 'invalid', foreground: 'f85149', fontStyle: 'bold' },
    { token: 'error', foreground: 'f85149', fontStyle: 'bold' },
    { token: 'warning', foreground: 'ffa657' },
    { token: 'info', foreground: '79c0ff' },
    
    // Markdown specific
    { token: 'emphasis', fontStyle: 'italic' },
    { token: 'strong', fontStyle: 'bold' },
    { token: 'header', foreground: '7ee787', fontStyle: 'bold' },
    { token: 'link', foreground: '79c0ff', fontStyle: 'underline' },
    
    // JSON specific
    { token: 'key', foreground: 'd2a8ff' },
    { token: 'property', foreground: 'd2a8ff' },
  ],
  colors: {
    // Editor background and foreground
    'editor.background': '#0d1117',
    'editor.foreground': '#c9d1d9',
    
    // Line highlighting
    'editor.lineHighlightBackground': '#161b22',
    'editor.lineHighlightBorder': '#21262d',
    
    // Selection
    'editor.selectionBackground': '#1f6feb',
    'editor.selectionHighlightBackground': '#1f6feb40',
    'editor.inactiveSelectionBackground': '#1f6feb30',
    
    // Line numbers
    'editorLineNumber.foreground': '#6e7681',
    'editorLineNumber.activeForeground': '#c9d1d9',
    
    // Gutter (where decorations appear)
    'editorGutter.background': '#0d1117',
    'editorGutter.modifiedBackground': '#ffa657',
    'editorGutter.addedBackground': '#7ee787',
    'editorGutter.deletedBackground': '#f85149',
    
    // Cursor
    'editorCursor.foreground': '#c9d1d9',
    'editorCursor.background': '#0d1117',
    
    // Whitespace
    'editorWhitespace.foreground': '#484f58',
    
    // Indentation guides
    'editorIndentGuide.background': '#21262d',
    'editorIndentGuide.activeBackground': '#6e7681',
    
    // Brackets
    'editorBracketMatch.background': '#1f6feb40',
    'editorBracketMatch.border': '#79c0ff',
    
    // Find/Replace
    'editor.findMatchBackground': '#ffa65780',
    'editor.findMatchHighlightBackground': '#ffa65740',
    'editor.findRangeHighlightBackground': '#ffa65720',
    
    // Scrollbar
    'scrollbarSlider.background': '#6e768180',
    'scrollbarSlider.hoverBackground': '#6e7681a0',
    'scrollbarSlider.activeBackground': '#6e7681c0',
    
    // Widget (hover cards, suggestions)
    'editorWidget.background': '#161b22',
    'editorWidget.border': '#30363d',
    'editorWidget.foreground': '#c9d1d9',
    'editorHoverWidget.background': '#161b22',
    'editorHoverWidget.border': '#30363d',
    
    // Suggest widget
    'editorSuggestWidget.background': '#161b22',
    'editorSuggestWidget.border': '#30363d',
    'editorSuggestWidget.foreground': '#c9d1d9',
    'editorSuggestWidget.selectedBackground': '#21262d',
    'editorSuggestWidget.highlightForeground': '#79c0ff',
  },
};

/**
 * Register custom themes with Monaco
 * 
 * This should be called once when Monaco is initialized.
 * Themes can then be switched using monaco.editor.setTheme()
 */
export function registerThemes(monaco: typeof Monaco): void {
  monaco.editor.defineTheme('pharos-light', lightTheme);
  monaco.editor.defineTheme('pharos-dark', darkTheme);
}

/**
 * Get theme name based on application theme
 * 
 * Maps application theme to Monaco theme name
 */
export function getMonacoTheme(appTheme: 'light' | 'dark'): string {
  return appTheme === 'light' ? 'pharos-light' : 'pharos-dark';
}

/**
 * Apply theme to Monaco editor instance
 * 
 * This allows theme switching without reloading the editor.
 * The editor will smoothly transition to the new theme.
 * 
 * @param monaco - Monaco instance
 * @param theme - Theme to apply ('light' or 'dark')
 */
export function applyTheme(monaco: typeof Monaco, theme: 'light' | 'dark'): void {
  const monacoTheme = getMonacoTheme(theme);
  monaco.editor.setTheme(monacoTheme);
}

/**
 * Get theme-specific gutter decoration colors
 * 
 * Returns colors for gutter decorations that match the current theme.
 * Used by decoration components to ensure visual consistency.
 */
export function getGutterDecorationColors(theme: 'light' | 'dark') {
  if (theme === 'light') {
    return {
      // Semantic chunks
      chunkBorder: 'rgba(209, 213, 218, 0.5)',
      chunkBackground: 'rgba(246, 248, 250, 0.5)',
      chunkHoverBorder: 'rgba(149, 157, 165, 0.8)',
      chunkHoverBackground: 'rgba(246, 248, 250, 0.8)',
      chunkSelectedBorder: '#005cc5',
      chunkSelectedBackground: 'rgba(0, 92, 197, 0.1)',
      
      // Quality badges
      qualityHigh: '#22863a',
      qualityMedium: '#e36209',
      qualityLow: '#cb2431',
      
      // Annotations
      annotationDefault: '#005cc5',
      annotationHighlight: 'rgba(0, 92, 197, 0.15)',
      annotationBorder: '#005cc5',
      
      // References
      referenceIcon: '#6a737d',
      referenceIconHover: '#24292e',
    };
  } else {
    return {
      // Semantic chunks
      chunkBorder: 'rgba(72, 79, 88, 0.5)',
      chunkBackground: 'rgba(22, 27, 34, 0.5)',
      chunkHoverBorder: 'rgba(110, 118, 129, 0.8)',
      chunkHoverBackground: 'rgba(22, 27, 34, 0.8)',
      chunkSelectedBorder: '#79c0ff',
      chunkSelectedBackground: 'rgba(121, 192, 255, 0.1)',
      
      // Quality badges
      qualityHigh: '#7ee787',
      qualityMedium: '#ffa657',
      qualityLow: '#f85149',
      
      // Annotations
      annotationDefault: '#79c0ff',
      annotationHighlight: 'rgba(121, 192, 255, 0.15)',
      annotationBorder: '#79c0ff',
      
      // References
      referenceIcon: '#8b949e',
      referenceIconHover: '#c9d1d9',
    };
  }
}

/**
 * Get language-specific theme enhancements
 * 
 * Some languages benefit from additional theme customization.
 * This function returns language-specific token rules.
 */
export function getLanguageThemeRules(
  language: string,
  baseTheme: 'light' | 'dark'
): Monaco.editor.ITokenThemeRule[] {
  const isLight = baseTheme === 'light';
  
  switch (language) {
    case 'python':
      return [
        { token: 'decorator', foreground: isLight ? '6f42c1' : 'd2a8ff' },
        { token: 'self', foreground: isLight ? 'e36209' : 'ffa657', fontStyle: 'italic' },
        { token: 'cls', foreground: isLight ? 'e36209' : 'ffa657', fontStyle: 'italic' },
      ];
      
    case 'typescript':
    case 'javascript':
      return [
        { token: 'type.identifier', foreground: isLight ? '22863a' : '7ee787' },
        { token: 'interface.name', foreground: isLight ? '22863a' : '7ee787', fontStyle: 'bold' },
        { token: 'this', foreground: isLight ? 'e36209' : 'ffa657', fontStyle: 'italic' },
      ];
      
    case 'rust':
      return [
        { token: 'lifetime', foreground: isLight ? '6f42c1' : 'd2a8ff', fontStyle: 'italic' },
        { token: 'macro', foreground: isLight ? '6f42c1' : 'd2a8ff', fontStyle: 'bold' },
      ];
      
    case 'go':
      return [
        { token: 'package', foreground: isLight ? 'd73a49' : 'ff7b72', fontStyle: 'bold' },
        { token: 'import', foreground: isLight ? 'd73a49' : 'ff7b72', fontStyle: 'bold' },
      ];
      
    default:
      return [];
  }
}
