/**
 * CodeEditorView Example
 * 
 * Demonstrates error handling integration in the Living Code Editor:
 * - Annotation API failures with cached data fallback
 * - Chunk API failures with line-based fallback
 * - Quality API failures with badge hiding
 * - Retry functionality
 * - Error dismissal
 */

import { useState } from 'react';
import { CodeEditorView } from './CodeEditorView';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { CodeFile } from './types';

// Sample code file
const sampleFile: CodeFile = {
  id: 'sample-1',
  resource_id: 'resource-sample',
  path: 'src/example.ts',
  name: 'example.ts',
  language: 'typescript',
  content: `/**
 * Example TypeScript file for demonstrating error handling
 */

interface User {
  id: string;
  name: string;
  email: string;
}

class UserService {
  private users: Map<string, User> = new Map();

  addUser(user: User): void {
    this.users.set(user.id, user);
  }

  getUser(id: string): User | undefined {
    return this.users.get(id);
  }

  getAllUsers(): User[] {
    return Array.from(this.users.values());
  }

  deleteUser(id: string): boolean {
    return this.users.delete(id);
  }
}

// Example usage
const service = new UserService();
service.addUser({
  id: '1',
  name: 'John Doe',
  email: 'john@example.com',
});

const user = service.getUser('1');
console.log(user);
`,
  size: 500,
  lines: 40,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

export function CodeEditorViewExample() {
  const [file] = useState<CodeFile>(sampleFile);

  return (
    <div className="space-y-6 p-6">
      <Card>
        <CardHeader>
          <CardTitle>Living Code Editor - Error Handling Demo</CardTitle>
          <CardDescription>
            This example demonstrates comprehensive error handling with graceful fallbacks
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <h3 className="text-lg font-semibold">Error Handling Features</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
              <li>
                <strong>Annotation Errors:</strong> Falls back to cached annotations with warning banner
              </li>
              <li>
                <strong>Chunk Errors:</strong> Falls back to line-based display (50 lines per chunk)
              </li>
              <li>
                <strong>Quality Errors:</strong> Automatically hides quality badges with warning
              </li>
              <li>
                <strong>Retry Support:</strong> All errors can be retried via banner buttons
              </li>
              <li>
                <strong>Error Dismissal:</strong> Users can dismiss errors to clear warnings
              </li>
            </ul>
          </div>

          <div className="space-y-2">
            <h3 className="text-lg font-semibold">Testing Error Scenarios</h3>
            <p className="text-sm text-muted-foreground">
              To test error handling, you can:
            </p>
            <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
              <li>Disconnect from network to trigger API failures</li>
              <li>Use browser DevTools to block specific API endpoints</li>
              <li>Mock API failures in tests (see CodeEditorView.error-handling.test.tsx)</li>
            </ul>
          </div>

          <div className="space-y-2">
            <h3 className="text-lg font-semibold">Expected Behavior</h3>
            <div className="space-y-2 text-sm">
              <div className="p-3 border rounded-lg bg-yellow-50 dark:bg-yellow-950/20">
                <strong className="text-yellow-700 dark:text-yellow-400">
                  Annotation API Failure (with cache):
                </strong>
                <p className="text-yellow-600 dark:text-yellow-500 mt-1">
                  Shows warning banner: "Using Cached Annotations - Unable to fetch latest annotations. Showing cached data."
                  <br />
                  Annotations remain visible from cache. Retry button available.
                </p>
              </div>

              <div className="p-3 border rounded-lg bg-red-50 dark:bg-red-950/20">
                <strong className="text-red-700 dark:text-red-400">
                  Annotation API Failure (no cache):
                </strong>
                <p className="text-red-600 dark:text-red-500 mt-1">
                  Shows error banner: "Annotation Error - Failed to fetch annotations. No cached data available."
                  <br />
                  No annotations displayed. Retry button available.
                </p>
              </div>

              <div className="p-3 border rounded-lg bg-yellow-50 dark:bg-yellow-950/20">
                <strong className="text-yellow-700 dark:text-yellow-400">
                  Chunk API Failure (with file content):
                </strong>
                <p className="text-yellow-600 dark:text-yellow-500 mt-1">
                  Shows warning banner: "Using Line-Based Display - AST chunking unavailable. Using line-based display."
                  <br />
                  Chunks generated from line numbers (50 lines per chunk). Retry button available.
                </p>
              </div>

              <div className="p-3 border rounded-lg bg-yellow-50 dark:bg-yellow-950/20">
                <strong className="text-yellow-700 dark:text-yellow-400">
                  Quality API Failure:
                </strong>
                <p className="text-yellow-600 dark:text-yellow-500 mt-1">
                  Shows warning banner: "Quality Data Unavailable - Failed to fetch quality data. Quality badges are hidden."
                  <br />
                  Quality badges automatically hidden. Retry button available.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Editor with Error Handling */}
      <Card>
        <CardHeader>
          <CardTitle>Code Editor</CardTitle>
          <CardDescription>
            Try disconnecting from network or blocking API endpoints to see error handling in action
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[600px] border rounded-lg overflow-hidden">
            <CodeEditorView file={file} />
          </div>
        </CardContent>
      </Card>

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>How to Test</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-semibold mb-2">1. Using Browser DevTools</h4>
            <ol className="list-decimal list-inside space-y-1 text-sm text-muted-foreground">
              <li>Open DevTools (F12)</li>
              <li>Go to Network tab</li>
              <li>Enable "Offline" mode or block specific endpoints</li>
              <li>Refresh the page or trigger API calls</li>
              <li>Observe error banners appearing</li>
              <li>Click "Retry" buttons to test retry functionality</li>
            </ol>
          </div>

          <div>
            <h4 className="font-semibold mb-2">2. Using Tests</h4>
            <pre className="p-3 bg-muted rounded-lg text-sm overflow-x-auto">
              <code>npm test -- CodeEditorView.error-handling.test.tsx</code>
            </pre>
          </div>

          <div>
            <h4 className="font-semibold mb-2">3. Manual Testing Checklist</h4>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Annotation API fails → Warning banner shows with cached data</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Chunk API fails → Warning banner shows with line-based fallback</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Quality API fails → Warning banner shows, badges hidden</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Retry button works for each error type</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Dismiss button clears error banners</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Multiple errors can be displayed simultaneously</span>
              </li>
              <li className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" />
                <span>Errors clear when file changes</span>
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
