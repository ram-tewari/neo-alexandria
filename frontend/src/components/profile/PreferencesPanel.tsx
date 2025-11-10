// Neo Alexandria 2.0 Frontend - Preferences Panel
// User preferences for subjects, languages, and recommendations

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { useAppStore } from '@/store';
import { Save, X, Plus } from 'lucide-react';
import { cn } from '@/utils/cn';

const AVAILABLE_LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'it', name: 'Italian' },
  { code: 'pt', name: 'Portuguese' },
  { code: 'zh', name: 'Chinese' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ar', name: 'Arabic' },
  { code: 'ru', name: 'Russian' },
];

const PreferencesPanel: React.FC = () => {
  const preferences = useAppStore((state) => state.preferences);
  const updatePreferences = useAppStore((state) => state.updatePreferences);
  
  const [subjects, setSubjects] = useState<string[]>(preferences.subjects);
  const [languages, setLanguages] = useState<string[]>(preferences.languages);
  const [newSubject, setNewSubject] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Track changes
  useEffect(() => {
    const subjectsChanged = JSON.stringify(subjects) !== JSON.stringify(preferences.subjects);
    const languagesChanged = JSON.stringify(languages) !== JSON.stringify(preferences.languages);
    setHasChanges(subjectsChanged || languagesChanged);
  }, [subjects, languages, preferences]);

  const handleAddSubject = () => {
    const trimmedSubject = newSubject.trim();
    if (trimmedSubject && !subjects.includes(trimmedSubject)) {
      setSubjects([...subjects, trimmedSubject]);
      setNewSubject('');
    }
  };

  const handleRemoveSubject = (subject: string) => {
    setSubjects(subjects.filter(s => s !== subject));
  };

  const handleToggleLanguage = (languageCode: string) => {
    if (languages.includes(languageCode)) {
      // Don't allow removing all languages
      if (languages.length > 1) {
        setLanguages(languages.filter(l => l !== languageCode));
      }
    } else {
      setLanguages([...languages, languageCode]);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    
    // Simulate async save
    await new Promise(resolve => setTimeout(resolve, 500));
    
    updatePreferences({
      subjects,
      languages,
    });
    
    setIsSaving(false);
    setHasChanges(false);
  };

  const handleReset = () => {
    setSubjects(preferences.subjects);
    setLanguages(preferences.languages);
    setNewSubject('');
    setHasChanges(false);
  };

  return (
    <div className="space-y-6">
      {/* Subject Preferences */}
      <div>
        <h3 className="text-lg font-semibold text-charcoal-grey-50 mb-2">
          Subject Preferences
        </h3>
        <p className="text-sm text-charcoal-grey-400 mb-4">
          Add subjects you're interested in to receive personalized recommendations
        </p>
        
        {/* Add Subject Input */}
        <div className="flex space-x-2 mb-4">
          <input
            type="text"
            value={newSubject}
            onChange={(e) => setNewSubject(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddSubject()}
            placeholder="Add a subject (e.g., Machine Learning)"
            className={cn(
              'flex-1 px-4 py-2 rounded-lg',
              'bg-charcoal-grey-800 border border-charcoal-grey-700',
              'text-charcoal-grey-50 placeholder-charcoal-grey-500',
              'focus:outline-none focus:ring-2 focus:ring-accent-blue-500 focus:border-transparent',
              'transition-colors duration-200'
            )}
          />
          <Button
            onClick={handleAddSubject}
            variant="primary"
            size="md"
            icon={<Plus />}
            disabled={!newSubject.trim()}
          >
            Add
          </Button>
        </div>

        {/* Subject Tags */}
        <div className="flex flex-wrap gap-2">
          {subjects.length === 0 ? (
            <p className="text-sm text-charcoal-grey-500 italic">
              No subjects added yet. Add subjects to personalize your experience.
            </p>
          ) : (
            subjects.map((subject) => (
              <span
                key={subject}
                className={cn(
                  'inline-flex items-center space-x-2 px-3 py-1.5 rounded-full',
                  'bg-accent-blue-500/20 text-accent-blue-300 border border-accent-blue-500/30',
                  'text-sm font-medium'
                )}
              >
                <span>{subject}</span>
                <button
                  onClick={() => handleRemoveSubject(subject)}
                  className="hover:text-accent-blue-100 transition-colors"
                  aria-label={`Remove ${subject}`}
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </span>
            ))
          )}
        </div>
      </div>

      {/* Language Preferences */}
      <div>
        <h3 className="text-lg font-semibold text-charcoal-grey-50 mb-2">
          Language Preferences
        </h3>
        <p className="text-sm text-charcoal-grey-400 mb-4">
          Select languages for content filtering and recommendations
        </p>
        
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {AVAILABLE_LANGUAGES.map((lang) => {
            const isSelected = languages.includes(lang.code);
            return (
              <button
                key={lang.code}
                onClick={() => handleToggleLanguage(lang.code)}
                className={cn(
                  'px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200',
                  'border focus:outline-none focus:ring-2 focus:ring-accent-blue-500',
                  isSelected
                    ? 'bg-accent-blue-500/20 border-accent-blue-500 text-accent-blue-300'
                    : 'bg-charcoal-grey-800 border-charcoal-grey-700 text-charcoal-grey-400 hover:border-charcoal-grey-600 hover:text-charcoal-grey-300'
                )}
              >
                {lang.name}
              </button>
            );
          })}
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
            Save Preferences
          </Button>
        </div>
      )}
    </div>
  );
};

export { PreferencesPanel };
