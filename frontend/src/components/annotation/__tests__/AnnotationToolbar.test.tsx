import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AnnotationToolbar } from '../AnnotationToolbar';
import { TextSelection } from '@/types/annotation';

const mockSelection: TextSelection = {
  text: 'This is selected text',
  start: 0,
  end: 21,
  rects: [],
};

describe('AnnotationToolbar', () => {
  it('displays selected text preview', () => {
    const onHighlight = vi.fn();
    const onNote = vi.fn();
    const onTag = vi.fn();
    const onClose = vi.fn();

    render(
      <AnnotationToolbar
        selection={mockSelection}
        onHighlight={onHighlight}
        onNote={onNote}
        onTag={onTag}
        onClose={onClose}
        position={{ x: 100, y: 100 }}
      />
    );

    expect(screen.getByText('"This is selected text"')).toBeInTheDocument();
  });

  it('shows color picker when highlight button is clicked', () => {
    const onHighlight = vi.fn();
    const onNote = vi.fn();
    const onTag = vi.fn();
    const onClose = vi.fn();

    render(
      <AnnotationToolbar
        selection={mockSelection}
        onHighlight={onHighlight}
        onNote={onNote}
        onTag={onTag}
        onClose={onClose}
        position={{ x: 100, y: 100 }}
      />
    );

    const highlightButton = screen.getByLabelText('Highlight');
    fireEvent.click(highlightButton);

    // Color picker should be visible
    const colorButtons = screen.getAllByRole('button').filter(btn => 
      btn.getAttribute('aria-label')?.includes('Highlight ')
    );
    expect(colorButtons.length).toBeGreaterThan(1);
  });

  it('calls onHighlight when color is selected', () => {
    const onHighlight = vi.fn();
    const onNote = vi.fn();
    const onTag = vi.fn();
    const onClose = vi.fn();

    render(
      <AnnotationToolbar
        selection={mockSelection}
        onHighlight={onHighlight}
        onNote={onNote}
        onTag={onTag}
        onClose={onClose}
        position={{ x: 100, y: 100 }}
      />
    );

    const highlightButton = screen.getByLabelText('Highlight');
    fireEvent.click(highlightButton);

    const yellowButton = screen.getByLabelText('Highlight Yellow');
    fireEvent.click(yellowButton);

    expect(onHighlight).toHaveBeenCalled();
  });

  it('calls onNote when note button is clicked', () => {
    const onHighlight = vi.fn();
    const onNote = vi.fn();
    const onTag = vi.fn();
    const onClose = vi.fn();

    render(
      <AnnotationToolbar
        selection={mockSelection}
        onHighlight={onHighlight}
        onNote={onNote}
        onTag={onTag}
        onClose={onClose}
        position={{ x: 100, y: 100 }}
      />
    );

    const noteButton = screen.getByLabelText('Add note');
    fireEvent.click(noteButton);

    expect(onNote).toHaveBeenCalled();
  });

  it('shows tag input when tag button is clicked', () => {
    const onHighlight = vi.fn();
    const onNote = vi.fn();
    const onTag = vi.fn();
    const onClose = vi.fn();

    render(
      <AnnotationToolbar
        selection={mockSelection}
        onHighlight={onHighlight}
        onNote={onNote}
        onTag={onTag}
        onClose={onClose}
        position={{ x: 100, y: 100 }}
      />
    );

    const tagButton = screen.getByLabelText('Add tags');
    fireEvent.click(tagButton);

    expect(screen.getByPlaceholderText('Add tag...')).toBeInTheDocument();
  });

  it('allows adding and removing tags', () => {
    const onHighlight = vi.fn();
    const onNote = vi.fn();
    const onTag = vi.fn();
    const onClose = vi.fn();

    render(
      <AnnotationToolbar
        selection={mockSelection}
        onHighlight={onHighlight}
        onNote={onNote}
        onTag={onTag}
        onClose={onClose}
        position={{ x: 100, y: 100 }}
      />
    );

    const tagButton = screen.getByLabelText('Add tags');
    fireEvent.click(tagButton);

    const input = screen.getByPlaceholderText('Add tag...');
    fireEvent.change(input, { target: { value: 'important' } });
    
    const addButton = screen.getByText('Add');
    fireEvent.click(addButton);

    expect(screen.getByText('important')).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const onHighlight = vi.fn();
    const onNote = vi.fn();
    const onTag = vi.fn();
    const onClose = vi.fn();

    render(
      <AnnotationToolbar
        selection={mockSelection}
        onHighlight={onHighlight}
        onNote={onNote}
        onTag={onTag}
        onClose={onClose}
        position={{ x: 100, y: 100 }}
      />
    );

    const closeButton = screen.getByLabelText('Close');
    fireEvent.click(closeButton);

    expect(onClose).toHaveBeenCalled();
  });
});
