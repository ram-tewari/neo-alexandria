/**
 * Monaco Editor theme configuration
 * 
 * Provides custom themes for light and dark modes that integrate
 * with the application's Tailwind theme system.
 */

import type * as Monaco from 'monaco-editor';

export const lightTheme: Monaco.editor.IStandaloneThemeData = {
  base: 'vs',
  inherit: true,
  rules: [
    { token: 'comment', foreground: '6a737d', fontStyle: 'italic' },
    { token: 'keyword', foreground: 'd73a49', fontStyle: 'bold' },
    { token: 'string', foreground: '032f62' },
    { token: 'number', foreground: '005cc5' },
    { token: 'function', foreground: '6f42c1' },
    { token: 'class', foreground: '22863a', fontStyle: 'bold' },
    { token: 'variable', foreground: 'e36209' },
  ],
  colors: {
    'editor.background': '#ffffff',
    'editor.foreground': '#24292e',
    'editor.lineHighlightBackground': '#f6f8fa',
    'editor.selectionBackground': '#c8e1ff',
    'editorLineNumber.foreground': '#959da5',
    'editorLineNumber.activeForeground': '#24292e',
    'editorGutter.background': '#ffffff',
    'editorCursor.foreground': '#24292e',
  },
};

export const darkTheme: Monaco.editor.IStandaloneThemeData = {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'comment', foreground: '8b949e', fontStyle: 'italic' },
    { token: 'keyword', foreground: 'ff7b72', fontStyle: 'bold' },
    { token: 'string', foreground: 'a5d6ff' },
    { token: 'number', foreground: '79c0ff' },
    { token: 'function', foreground: 'd2a8ff' },
    { token: 'class', foreground: '7ee787', fontStyle: 'bold' },
    { token: 'variable', foreground: 'ffa657' },
  ],
  colors: {
    'editor.background': '#0d1117',
    'editor.foreground': '#c9d1d9',
    'editor.lineHighlightBackground': '#161b22',
    'editor.selectionBackground': '#1f6feb',
    'editorLineNumber.foreground': '#6e7681',
    'editorLineNumber.activeForeground': '#c9d1d9',
    'editorGutter.background': '#0d1117',
    'editorCursor.foreground': '#c9d1d9',
  },
};

/**
 * Register custom themes with Monaco
 */
export function registerThemes(monaco: typeof Monaco) {
  monaco.editor.defineTheme('pharos-light', lightTheme);
  monaco.editor.defineTheme('pharos-dark', darkTheme);
}

/**
 * Get theme name based on application theme
 */
export function getMonacoTheme(appTheme: 'light' | 'dark'): string {
  return appTheme === 'light' ? 'pharos-light' : 'pharos-dark';
}
