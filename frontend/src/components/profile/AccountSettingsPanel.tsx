// Neo Alexandria 2.0 Frontend - Account Settings Panel
// User account settings including theme, view preferences, and user ID

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { useAppStore } from '@/store';
import { Save, Sun, Moon, Grid, List } from 'lucide-react';
import { cn } from '@/utils/cn';

const ITEMS_PER_PAGE_OPTIONS = [10, 25, 50, 100];

const AccountSettingsPanel: React.FC = () => {
  const userId = useAppStore((state) => state.userId);
  const preferences = useAppStore((state) => state.preferences);
  const setUserId = useAppStore((state) => state.setUserId);
  const updatePreferences = useAppStore((state) => state.updatePreferences);
  
  const [localUserId, setLocalUserId] = useState(userId || '');
  const [theme, setTheme] = useState(preferences.display.theme);
  const [defaultView, setDefaultView] = useState(preferences.display.defaultView);
  const [itemsPerPage, setItemsPerPage] = useState(preferences.display.itemsPerPage);
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Track changes
  useEffect(() => {
    const userIdChanged = localUserId !== (userId || '');
    const themeChanged = theme !== preferences.display.theme;
    const viewChanged = defaultView !== preferences.display.defaultView;
    const itemsChanged = itemsPerPage !== preferences.display.itemsPerPage;
    
    setHasChanges(userIdChanged || themeChanged || viewChanged || itemsChanged);
  }, [localUserId, theme, defaultView, itemsPerPage, userId, preferences]);

  const handleSave = async () => {
    setIsSaving(true);
    
    // Simulate async save
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Update user ID
    setUserId(localUserId || null);
    
    // Update display preferences
    updatePreferences({
      display: {
        theme,
        defaultView,
        itemsPerPage,
      },
    });
    
    setIsSaving(false);
    setHasChanges(false);
  };

  const handleReset = () => {
    setLocalUserId(userId || '');
    setTheme(preferences.display.theme);
    setDefaultView(preferences.display.defaultView);
    setItemsPerPage(preferences.display.itemsPerPage);
    setHasChanges(false);
  };

  return (
    <div className="space-y-6">
      {/* User ID */}
      <div>
        <h3 className="text-lg font-semibold text-charcoal-grey-50 mb-2">
          User ID
        </h3>
        <p className="text-sm text-charcoal-grey-400 mb-4">
          Set your user ID for personalized features (demo purposes)
        </p>
        
        <input
          type="text"
          value={localUserId}
          onChange={(e) => setLocalUserId(e.target.value)}
          placeholder="Enter your user ID"
          className={cn(
            'w-full max-w-md px-4 py-2 rounded-lg',
            'bg-charcoal-grey-800 border border-charcoal-grey-700',
            'text-charcoal-grey-50 placeholder-charcoal-grey-500',
            'focus:outline-none focus:ring-2 focus:ring-accent-blue-500 focus:border-transparent',
            'transition-colors duration-200'
          )}
        />
      </div>

      {/* Theme Selection */}
      <div>
        <h3 className="text-lg font-semibold text-charcoal-grey-50 mb-2">
          Theme
        </h3>
        <p className="text-sm text-charcoal-grey-400 mb-4">
          Choose your preferred color theme
        </p>
        
        <div className="flex space-x-3">
          <button
            onClick={() => setTheme('dark')}
            className={cn(
              'flex items-center space-x-3 px-6 py-4 rounded-lg transition-all duration-200',
              'border focus:outline-none focus:ring-2 focus:ring-accent-blue-500',
              theme === 'dark'
                ? 'bg-accent-blue-500/20 border-accent-blue-500 text-accent-blue-300'
                : 'bg-charcoal-grey-800 border-charcoal-grey-700 text-charcoal-grey-400 hover:border-charcoal-grey-600'
            )}
          >
            <Moon className="w-5 h-5" />
            <div className="text-left">
              <div className="font-medium">Dark</div>
              <div className="text-xs opacity-75">Easy on the eyes</div>
            </div>
          </button>
          
          <button
            onClick={() => setTheme('light')}
            className={cn(
              'flex items-center space-x-3 px-6 py-4 rounded-lg transition-all duration-200',
              'border focus:outline-none focus:ring-2 focus:ring-accent-blue-500',
              theme === 'light'
                ? 'bg-accent-blue-500/20 border-accent-blue-500 text-accent-blue-300'
                : 'bg-charcoal-grey-800 border-charcoal-grey-700 text-charcoal-grey-400 hover:border-charcoal-grey-600'
            )}
          >
            <Sun className="w-5 h-5" />
            <div className="text-left">
              <div className="font-medium">Light</div>
              <div className="text-xs opacity-75">Bright and clear</div>
            </div>
          </button>
        </div>
      </div>

      {/* Default View */}
      <div>
        <h3 className="text-lg font-semibold text-charcoal-grey-50 mb-2">
          Default View
        </h3>
        <p className="text-sm text-charcoal-grey-400 mb-4">
          Choose how resources are displayed by default
        </p>
        
        <div className="flex space-x-3">
          <button
            onClick={() => setDefaultView('grid')}
            className={cn(
              'flex items-center space-x-3 px-6 py-4 rounded-lg transition-all duration-200',
              'border focus:outline-none focus:ring-2 focus:ring-accent-blue-500',
              defaultView === 'grid'
                ? 'bg-accent-blue-500/20 border-accent-blue-500 text-accent-blue-300'
                : 'bg-charcoal-grey-800 border-charcoal-grey-700 text-charcoal-grey-400 hover:border-charcoal-grey-600'
            )}
          >
            <Grid className="w-5 h-5" />
            <div className="text-left">
              <div className="font-medium">Grid</div>
              <div className="text-xs opacity-75">Card layout</div>
            </div>
          </button>
          
          <button
            onClick={() => setDefaultView('list')}
            className={cn(
              'flex items-center space-x-3 px-6 py-4 rounded-lg transition-all duration-200',
              'border focus:outline-none focus:ring-2 focus:ring-accent-blue-500',
              defaultView === 'list'
                ? 'bg-accent-blue-500/20 border-accent-blue-500 text-accent-blue-300'
                : 'bg-charcoal-grey-800 border-charcoal-grey-700 text-charcoal-grey-400 hover:border-charcoal-grey-600'
            )}
          >
            <List className="w-5 h-5" />
            <div className="text-left">
              <div className="font-medium">List</div>
              <div className="text-xs opacity-75">Compact rows</div>
            </div>
          </button>
        </div>
      </div>

      {/* Items Per Page */}
      <div>
        <h3 className="text-lg font-semibold text-charcoal-grey-50 mb-2">
          Items Per Page
        </h3>
        <p className="text-sm text-charcoal-grey-400 mb-4">
          Number of items to display per page
        </p>
        
        <div className="flex space-x-2">
          {ITEMS_PER_PAGE_OPTIONS.map((option) => (
            <button
              key={option}
              onClick={() => setItemsPerPage(option)}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                'border focus:outline-none focus:ring-2 focus:ring-accent-blue-500',
                itemsPerPage === option
                  ? 'bg-accent-blue-500/20 border-accent-blue-500 text-accent-blue-300'
                  : 'bg-charcoal-grey-800 border-charcoal-grey-700 text-charcoal-grey-400 hover:border-charcoal-grey-600'
              )}
            >
              {option}
            </button>
          ))}
        </div>
      </div>

      {/* Save Actions */}
      {hasChanges && (
        <div className="flex items-center justify-end space-x-3 pt-4 border-t border-charcoal-grey-700">
          <Button
            onClick={handleReset}
            variant="ghost"
            size="md"
          >
            Reset
          </Button>
          <Button
            onClick={handleSave}
            variant="primary"
            size="md"
            loading={isSaving}
            icon={<Save />}
          >
            Save Settings
          </Button>
        </div>
      )}
    </div>
  );
};

export { AccountSettingsPanel };
