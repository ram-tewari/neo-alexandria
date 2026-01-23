/**
 * HoverCardProvider Component Tests
 * 
 * Tests hover detection, debouncing, data fetching, display, and fallback behavior.
 * 
 * Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import { HoverCardProvider } from '../HoverCardProvider';
import * as monaco from 'monaco-editor';
import { editorApi } from '@/lib/api/editor';

// Mock Monaco Editor
vi.mock('monaco-editor', () => ({
  editor: {
    MouseTargetType: {
      CONTENT_TEXT: 6,
      GUTTER_GLYPH_MARGIN: 2,
      OUTSIDE_EDITOR: 0,
    },
  },
  Position: class Position {
    constructor(public lineNumber: number, public column: number) {}
  },
  languages: {
    getHoverProvider: vi.fn(),
    getHover: vi.fn(),
  },
}));

// Mock editor API
vi.mock('@/lib/api/editor', () => ({
  editorApi: {
    getNode2VecSummary: vi.fn(),
  },
}));

// Mock UI components
vi.mock('@/components/ui/hover-card', () => ({
  HoverCard: ({ children, open }: any) => open ? <div data-testid="hover-card">{children}</div> : null,
  HoverCardTrigger: ({ children }: any) => <div>{children}</div>,
  HoverCardContent: ({ children }: any) => <div data-testid="hover-card-content">{children}</div>,
}));

vi.mock('@/components/ui/skeleton', () => ({
  Skeleton: ({ className }: any) => <div data-testid="skeleton" className={className} />,
}));

vi.mock('@/components/ui/alert', () => ({
  Alert: ({ children }: any) => <div data-testid="alert">{children}</div>,
  AlertDescription: ({ children }: any) => <div>{children}</div>,
}));

vi.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick }: any) => (
    <button onClick={onClick} data-testid="button">{children}</button>
  ),
}));

describe('HoverCardProvider', () => {
  let mockEditor: any;
  let mouseListeners: any[] = [];
  let blurListeners: any[] = [];

  beforeEach(() => {
    vi.clearAllMocks();
    mouseListeners = [];
    blurListeners = [];

    // Create mock editor
    mockEditor = {
      onMouseMove: vi.fn((callback) => {
        mouseListeners.push(callback);
        return { dispose: vi.fn() };
      }),
      onDidBlurEditorText: vi.fn((callback) => {
        blurListeners.push(callback);
        return { dispose: vi.fn() };
      }),
      getModel: vi.fn(() => ({
        getWordAtPosition: vi.fn((pos) => ({
          word: 'testFunction',
          startColumn: 1,
          endColumn: 13,
        })),
        getLanguageId: vi.fn(() => 'typescript'),
      })),
    };
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  describe('Hover Detection', () => {
    it('should detect symbol under cursor on hover', async () => {
      const mockNode2VecResponse = {
        summary: 'Test function summary',
        connections: [],
      };
      vi.mocked(editorApi.getNode2VecSummary).mockResolvedValue(mockNode2VecResponse);

      render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      // Simulate mouse move over text
      const mouseEvent = {
        target: {
          type: monaco.editor.MouseTargetType.CONTENT_TEXT,
          position: new monaco.Position(10, 5),
        },
      };

      act(() => {
        mouseListeners[0](mouseEvent);
      });

      // Wait for debounce and API call
      await waitFor(() => {
        expect(editorApi.getNode2VecSummary).toHaveBeenCalledWith('test-resource', 'testFunction');
      }, { timeout: 1000 });
    });

    it('should debounce hover events by 300ms', async () => {
      const mockNode2VecResponse = {
        summary: 'Test function summary',
        connections: [],
      };
      vi.mocked(editorApi.getNode2VecSummary).mockResolvedValue(mockNode2VecResponse);

      render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      const mouseEvent = {
        target: {
          type: monaco.editor.MouseTargetType.CONTENT_TEXT,
          position: new monaco.Position(10, 5),
        },
      };

      // Trigger multiple hover events rapidly
      mouseListeners[0](mouseEvent);
      await new Promise(resolve => setTimeout(resolve, 100));
      mouseListeners[0](mouseEvent);
      await new Promise(resolve => setTimeout(resolve, 100));
      mouseListeners[0](mouseEvent);

      // Should not have called API yet
      expect(editorApi.getNode2VecSummary).not.toHaveBeenCalled();

      // Wait for debounce to complete
      await waitFor(() => {
        expect(editorApi.getNode2VecSummary).toHaveBeenCalledTimes(1);
      }, { timeout: 1000 });
    });

    it('should not trigger hover on non-text targets', async () => {
      render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      // Simulate mouse move over gutter
      const mouseEvent = {
        target: {
          type: monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN,
          position: new monaco.Position(10, 5),
        },
      };

      mouseListeners[0](mouseEvent);
      
      // Wait to ensure no API call is made
      await new Promise(resolve => setTimeout(resolve, 400));
      expect(editorApi.getNode2VecSummary).not.toHaveBeenCalled();
    });

    it('should not trigger hover when no symbol detected', async () => {
      mockEditor.getModel = vi.fn(() => ({
        getWordAtPosition: vi.fn(() => null),
        getLanguageId: vi.fn(() => 'typescript'),
      }));

      render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      const mouseEvent = {
        target: {
          type: monaco.editor.MouseTargetType.CONTENT_TEXT,
          position: new monaco.Position(10, 5),
        },
      };

      mouseListeners[0](mouseEvent);
      
      // Wait to ensure no API call is made
      await new Promise(resolve => setTimeout(resolve, 400));
      expect(editorApi.getNode2VecSummary).not.toHaveBeenCalled();
    });
  });

  describe('Data Fetching', () => {
    it('should fetch Node2Vec summary on hover', async () => {
      const mockNode2VecResponse = {
        summary: 'Test function that does something',
        connections: [
          {
            name: 'helperFunction',
            type: 'function' as const,
            relationship: 'calls' as const,
            file: 'utils.ts',
          },
        ],
      };
      vi.mocked(editorApi.getNode2VecSummary).mockResolvedValue(mockNode2VecResponse);

      render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      const mouseEvent = {
        target: {
          type: monaco.editor.MouseTargetType.CONTENT_TEXT,
          position: new monaco.Position(10, 5),
        },
      };

      mouseListeners[0](mouseEvent);

      await waitFor(() => {
        expect(screen.getByText('Test function that does something')).toBeInTheDocument();
      }, { timeout: 1000 });
    });

    it('should show loading skeleton while fetching', async () => {
      // Make API call take time
      vi.mocked(editorApi.getNode2VecSummary).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({
          summary: 'Test summary',
          connections: [],
        }), 500))
      );

      render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      const mouseEvent = {
        target: {
          type: monaco.editor.MouseTargetType.CONTENT_TEXT,
          position: new monaco.Position(10, 5),
        },
      };

      mouseListeners[0](mouseEvent);

      await waitFor(() => {
        expect(screen.getAllByTestId('skeleton').length).toBeGreaterThan(0);
      }, { timeout: 1000 });
    });

    it('should not refetch for same symbol', async () => {
      const mockNode2VecResponse = {
        summary: 'Test function summary',
        connections: [],
      };
      vi.mocked(editorApi.getNode2VecSummary).mockResolvedValue(mockNode2VecResponse);

      render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      const mouseEvent = {
        target: {
          type: monaco.editor.MouseTargetType.CONTENT_TEXT,
          position: new monaco.Position(10, 5),
        },
      };

      // First hover
      mouseListeners[0](mouseEvent);

      await waitFor(() => {
        expect(editorApi.getNode2VecSummary).toHaveBeenCalledTimes(1);
      }, { timeout: 1000 });

      // Second hover on same symbol
      mouseListeners[0](mouseEvent);
      
      // Wait a bit to ensure no second call
      await new Promise(resolve => setTimeout(resolve, 400));

      // Should not call API again
      expect(editorApi.getNode2VecSummary).toHaveBeenCalledTimes(1);
    });
  });

  describe('Hover Card Display', () => {
    it('should display Node2Vec summary', async () => {
      const mockNode2VecResponse = {
        summary: 'This function processes user input',
        connections: [],
      };
      vi.mocked(editorApi.getNode2VecSummary).mockResolvedValue(mockNode2VecResponse);

      render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      const mouseEvent = {
        target: {
          type: monaco.editor.MouseTargetType.CONTENT_TEXT,
          position: new monaco.Position(10, 5),
        },
      };

      mouseListeners[0](mouseEvent);

      await waitFor(() => {
        expect(screen.getByText('This function processes user input')).toBeInTheDocument();
      }, { timeout: 1000 });
    });

    it('should display 1-hop graph connections', async () => {
      const mockNode2VecResponse = {
        summary: 'Test function',
        connections: [
          {
            name: 'helperFunction',
            type: 'function' as const,
            relationship: 'calls' as const,
            file: 'utils.ts',
          },
          {
            name: 'DataClass',
            type: 'class' as const,
            relationship: 'uses' as const,
            file: 'models.ts',
          },
        ],
      };
      vi.mocked(editorApi.getNode2VecSummary).mockResolvedValue(mockNode2VecResponse);

      render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      const mouseEvent = {
        target: {
          type: monaco.editor.MouseTargetType.CONTENT_TEXT,
          position: new monaco.Position(10, 5),
        },
      };

      mouseListeners[0](mouseEvent);

      await waitFor(() => {
        expect(screen.getByText('helperFunction')).toBeInTheDocument();
        expect(screen.getByText('DataClass')).toBeInTheDocument();
        expect(screen.getByText(/calls.*utils\.ts/)).toBeInTheDocument();
        expect(screen.getByText(/uses.*models\.ts/)).toBeInTheDocument();
      }, { timeout: 1000 });
    });

    it('should display symbol name', async () => {
      const mockNode2VecResponse = {
        summary: 'Test summary',
        connections: [],
      };
      vi.mocked(editorApi.getNode2VecSummary).mockResolvedValue(mockNode2VecResponse);

      render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      const mouseEvent = {
        target: {
          type: monaco.editor.MouseTargetType.CONTENT_TEXT,
          position: new monaco.Position(10, 5),
        },
      };

      mouseListeners[0](mouseEvent);

      await waitFor(() => {
        expect(screen.getByText('testFunction')).toBeInTheDocument();
      }, { timeout: 1000 });
    });
  });

  describe('Fallback Behavior', () => {
    it('should fall back to Monaco IntelliSense on API error', async () => {
      vi.mocked(editorApi.getNode2VecSummary).mockRejectedValue(
        new Error('API unavailable')
      );

      // Mock Monaco hover provider
      vi.mocked(monaco.languages.getHover).mockResolvedValue({
        contents: [{ value: 'function testFunction(): void' }],
        range: null as any,
      });

      render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      const mouseEvent = {
        target: {
          type: monaco.editor.MouseTargetType.CONTENT_TEXT,
          position: new monaco.Position(10, 5),
        },
      };

      mouseListeners[0](mouseEvent);

      // Should show error message and fallback info
      await waitFor(() => {
        expect(screen.getByText(/Unable to load Node2Vec summary/)).toBeInTheDocument();
        expect(screen.getByText('Symbol: testFunction')).toBeInTheDocument();
      }, { timeout: 1000 });
    });

    it('should display error message on API failure', async () => {
      vi.mocked(editorApi.getNode2VecSummary).mockRejectedValue(
        new Error('API unavailable')
      );

      render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      const mouseEvent = {
        target: {
          type: monaco.editor.MouseTargetType.CONTENT_TEXT,
          position: new monaco.Position(10, 5),
        },
      };

      mouseListeners[0](mouseEvent);

      await waitFor(() => {
        expect(screen.getByText(/Unable to load Node2Vec summary/)).toBeInTheDocument();
      }, { timeout: 1000 });
    });

    it('should show basic symbol info when Monaco hover unavailable', async () => {
      vi.mocked(editorApi.getNode2VecSummary).mockRejectedValue(
        new Error('API unavailable')
      );

      vi.mocked(monaco.languages.getHover).mockResolvedValue(null as any);

      render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      const mouseEvent = {
        target: {
          type: monaco.editor.MouseTargetType.CONTENT_TEXT,
          position: new monaco.Position(10, 5),
        },
      };

      mouseListeners[0](mouseEvent);

      await waitFor(() => {
        expect(screen.getByText('Symbol: testFunction')).toBeInTheDocument();
      }, { timeout: 1000 });
    });
  });

  describe('Cleanup', () => {
    it('should close hover card on editor blur', async () => {
      const mockNode2VecResponse = {
        summary: 'Test summary',
        connections: [],
      };
      vi.mocked(editorApi.getNode2VecSummary).mockResolvedValue(mockNode2VecResponse);

      render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      const mouseEvent = {
        target: {
          type: monaco.editor.MouseTargetType.CONTENT_TEXT,
          position: new monaco.Position(10, 5),
        },
      };

      mouseListeners[0](mouseEvent);

      await waitFor(() => {
        expect(screen.getByTestId('hover-card')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Trigger blur
      act(() => {
        blurListeners[0]();
      });

      await waitFor(() => {
        expect(screen.queryByTestId('hover-card')).not.toBeInTheDocument();
      });
    });

    it('should dispose listeners on unmount', () => {
      const { unmount } = render(
        <HoverCardProvider
          editor={mockEditor}
          resourceId="test-resource"
        />
      );

      const mouseDispose = mockEditor.onMouseMove.mock.results[0].value.dispose;
      const blurDispose = mockEditor.onDidBlurEditorText.mock.results[0].value.dispose;

      unmount();

      expect(mouseDispose).toHaveBeenCalled();
      expect(blurDispose).toHaveBeenCalled();
    });
  });
});
