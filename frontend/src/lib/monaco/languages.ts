/**
 * Monaco Editor language configuration
 * 
 * Provides language detection and configuration for supported
 * programming languages.
 */

/**
 * Map file extensions to Monaco language IDs
 */
export const extensionToLanguage: Record<string, string> = {
  // JavaScript/TypeScript
  js: 'javascript',
  jsx: 'javascript',
  ts: 'typescript',
  tsx: 'typescript',
  mjs: 'javascript',
  cjs: 'javascript',

  // Python
  py: 'python',
  pyw: 'python',
  pyi: 'python',

  // Web
  html: 'html',
  htm: 'html',
  css: 'css',
  scss: 'scss',
  sass: 'sass',
  less: 'less',

  // Data formats
  json: 'json',
  jsonc: 'json',
  yaml: 'yaml',
  yml: 'yaml',
  xml: 'xml',
  toml: 'toml',

  // Markdown
  md: 'markdown',
  markdown: 'markdown',

  // Shell
  sh: 'shell',
  bash: 'shell',
  zsh: 'shell',

  // C/C++
  c: 'c',
  h: 'c',
  cpp: 'cpp',
  hpp: 'cpp',
  cc: 'cpp',
  cxx: 'cpp',

  // Java
  java: 'java',

  // Go
  go: 'go',

  // Rust
  rs: 'rust',

  // Ruby
  rb: 'ruby',

  // PHP
  php: 'php',

  // SQL
  sql: 'sql',

  // Other
  txt: 'plaintext',
  log: 'plaintext',
};

/**
 * Detect language from file path
 */
export function detectLanguage(filePath: string): string {
  const extension = filePath.split('.').pop()?.toLowerCase();
  return extension ? extensionToLanguage[extension] || 'plaintext' : 'plaintext';
}

/**
 * Get human-readable language name
 */
export function getLanguageName(languageId: string): string {
  const names: Record<string, string> = {
    javascript: 'JavaScript',
    typescript: 'TypeScript',
    python: 'Python',
    html: 'HTML',
    css: 'CSS',
    scss: 'SCSS',
    sass: 'Sass',
    less: 'Less',
    json: 'JSON',
    yaml: 'YAML',
    xml: 'XML',
    toml: 'TOML',
    markdown: 'Markdown',
    shell: 'Shell',
    c: 'C',
    cpp: 'C++',
    java: 'Java',
    go: 'Go',
    rust: 'Rust',
    ruby: 'Ruby',
    php: 'PHP',
    sql: 'SQL',
    plaintext: 'Plain Text',
  };

  return names[languageId] || languageId;
}

/**
 * Check if language supports semantic highlighting
 */
export function supportsSemanticHighlighting(languageId: string): boolean {
  const supported = [
    'javascript',
    'typescript',
    'python',
    'java',
    'cpp',
    'c',
    'go',
    'rust',
  ];
  return supported.includes(languageId);
}
