import { useEffect, useRef } from 'react';
import './ResourceTabs.css';

interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
}

interface ResourceTabsProps {
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

const tabs: Tab[] = [
  {
    id: 'content',
    label: 'Content',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 2h10a1 1 0 011 1v10a1 1 0 01-1 1H3a1 1 0 01-1-1V3a1 1 0 011-1zm1 2v8h8V4H4z" fill="currentColor" />
      </svg>
    ),
  },
  {
    id: 'annotations',
    label: 'Annotations',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M2 3a1 1 0 011-1h10a1 1 0 011 1v7a1 1 0 01-1 1H8l-3 3v-3H3a1 1 0 01-1-1V3z" fill="currentColor" />
      </svg>
    ),
  },
  {
    id: 'metadata',
    label: 'Metadata',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 1a7 7 0 100 14A7 7 0 008 1zm0 3a1 1 0 110 2 1 1 0 010-2zm1 8H7V7h2v5z" fill="currentColor" />
      </svg>
    ),
  },
  {
    id: 'graph',
    label: 'Graph',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 2a2 2 0 100 4 2 2 0 000-4zM3 11a2 2 0 100 4 2 2 0 000-4zm10 0a2 2 0 100 4 2 2 0 000-4zM8 6L3 11m5-5l5 5" stroke="currentColor" strokeWidth="1.5" />
      </svg>
    ),
  },
  {
    id: 'quality',
    label: 'Quality',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 1l2 5h5l-4 3 1.5 5L8 11l-4.5 3L5 9 1 6h5l2-5z" fill="currentColor" />
      </svg>
    ),
  },
];

/**
 * ResourceTabs - Tab navigation component with keyboard support
 * 
 * Features:
 * - ARIA-compliant tab interface
 * - Keyboard navigation (arrow keys)
 * - URL sync via parent component
 * - Visual active state
 */
export const ResourceTabs: React.FC<ResourceTabsProps> = ({ activeTab, onTabChange }) => {
  const tabListRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!tabListRef.current?.contains(document.activeElement)) {
        return;
      }

      const currentIndex = tabs.findIndex(tab => tab.id === activeTab);
      let nextIndex = currentIndex;

      switch (e.key) {
        case 'ArrowLeft':
          e.preventDefault();
          nextIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
          break;
        case 'ArrowRight':
          e.preventDefault();
          nextIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
          break;
        case 'Home':
          e.preventDefault();
          nextIndex = 0;
          break;
        case 'End':
          e.preventDefault();
          nextIndex = tabs.length - 1;
          break;
        default:
          return;
      }

      if (nextIndex !== currentIndex) {
        onTabChange(tabs[nextIndex].id);
        // Focus the new tab
        const tabButton = tabListRef.current?.querySelector(
          `[data-tab-id="${tabs[nextIndex].id}"]`
        ) as HTMLButtonElement;
        tabButton?.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [activeTab, onTabChange]);

  return (
    <div className="resource-tabs" ref={tabListRef}>
      <div
        role="tablist"
        aria-label="Resource information tabs"
        className="tab-list"
      >
        {tabs.map((tab) => {
          const isActive = tab.id === activeTab;
          
          return (
            <button
              key={tab.id}
              role="tab"
              id={`tab-${tab.id}`}
              data-tab-id={tab.id}
              aria-selected={isActive}
              aria-controls={`panel-${tab.id}`}
              tabIndex={isActive ? 0 : -1}
              onClick={() => onTabChange(tab.id)}
              className={`tab-button ${isActive ? 'active' : ''}`}
            >
              {tab.icon && <span className="tab-icon">{tab.icon}</span>}
              <span className="tab-label">{tab.label}</span>
            </button>
          );
        })}
      </div>
      <div className="tab-indicator" />
    </div>
  );
};
