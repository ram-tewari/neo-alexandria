// Neo Alexandria 2.0 Frontend - Notification Preferences Panel
// User notification preferences for various system events

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { useAppStore } from '@/store';
import { Save, Bell, CheckCircle, TrendingUp, Lightbulb } from 'lucide-react';
import { cn } from '@/utils/cn';
import { motion } from 'framer-motion';

interface NotificationSetting {
  id: keyof typeof defaultNotifications;
  label: string;
  description: string;
  icon: React.ReactNode;
}

const defaultNotifications = {
  ingestion_complete: true,
  quality_updates: true,
  recommendations: true,
};

const notificationSettings: NotificationSetting[] = [
  {
    id: 'ingestion_complete',
    label: 'Ingestion Complete',
    description: 'Get notified when resource ingestion and processing is complete',
    icon: <CheckCircle className="w-5 h-5" />,
  },
  {
    id: 'quality_updates',
    label: 'Quality Updates',
    description: 'Receive notifications about quality score changes and improvements',
    icon: <TrendingUp className="w-5 h-5" />,
  },
  {
    id: 'recommendations',
    label: 'Recommendations',
    description: 'Get personalized resource and collection recommendations',
    icon: <Lightbulb className="w-5 h-5" />,
  },
];

const NotificationPreferencesPanel: React.FC = () => {
  const preferences = useAppStore((state) => state.preferences);
  const updatePreferences = useAppStore((state) => state.updatePreferences);
  
  const [notifications, setNotifications] = useState(preferences.notifications);
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Track changes
  useEffect(() => {
    const changed = JSON.stringify(notifications) !== JSON.stringify(preferences.notifications);
    setHasChanges(changed);
  }, [notifications, preferences.notifications]);

  const handleToggle = (key: keyof typeof defaultNotifications) => {
    setNotifications({
      ...notifications,
      [key]: !notifications[key],
    });
  };

  const handleSave = async () => {
    setIsSaving(true);
    
    // Simulate async save
    await new Promise(resolve => setTimeout(resolve, 500));
    
    updatePreferences({
      notifications,
    });
    
    setIsSaving(false);
    setHasChanges(false);
  };

  const handleReset = () => {
    setNotifications(preferences.notifications);
    setHasChanges(false);
  };

  const handleEnableAll = () => {
    setNotifications({
      ingestion_complete: true,
      quality_updates: true,
      recommendations: true,
    });
  };

  const handleDisableAll = () => {
    setNotifications({
      ingestion_complete: false,
      quality_updates: false,
      recommendations: false,
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold text-charcoal-grey-50 mb-2">
            Notification Preferences
          </h3>
          <p className="text-sm text-charcoal-grey-400">
            Choose which notifications you want to receive
          </p>
        </div>
        
        <div className="flex space-x-2">
          <Button
            onClick={handleEnableAll}
            variant="ghost"
            size="sm"
          >
            Enable All
          </Button>
          <Button
            onClick={handleDisableAll}
            variant="ghost"
            size="sm"
          >
            Disable All
          </Button>
        </div>
      </div>

      {/* Notification Settings */}
      <div className="space-y-4">
        {notificationSettings.map((setting) => {
          const isEnabled = notifications[setting.id];
          
          return (
            <motion.div
              key={setting.id}
              className={cn(
                'flex items-start space-x-4 p-4 rounded-lg border transition-all duration-200',
                isEnabled
                  ? 'bg-accent-blue-500/10 border-accent-blue-500/30'
                  : 'bg-charcoal-grey-800 border-charcoal-grey-700'
              )}
              whileHover={{ scale: 1.01 }}
              transition={{ duration: 0.15 }}
            >
              {/* Icon */}
              <div className={cn(
                'flex-shrink-0 p-2 rounded-lg',
                isEnabled
                  ? 'bg-accent-blue-500/20 text-accent-blue-400'
                  : 'bg-charcoal-grey-700 text-charcoal-grey-400'
              )}>
                {setting.icon}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <h4 className={cn(
                  'text-sm font-medium mb-1',
                  isEnabled ? 'text-charcoal-grey-50' : 'text-charcoal-grey-300'
                )}>
                  {setting.label}
                </h4>
                <p className="text-sm text-charcoal-grey-400">
                  {setting.description}
                </p>
              </div>

              {/* Toggle Switch */}
              <button
                onClick={() => handleToggle(setting.id)}
                className={cn(
                  'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent',
                  'transition-colors duration-200 ease-in-out',
                  'focus:outline-none focus:ring-2 focus:ring-accent-blue-500 focus:ring-offset-2 focus:ring-offset-charcoal-grey-900',
                  isEnabled ? 'bg-accent-blue-500' : 'bg-charcoal-grey-700'
                )}
                role="switch"
                aria-checked={isEnabled}
                aria-label={`Toggle ${setting.label}`}
              >
                <span
                  className={cn(
                    'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0',
                    'transition duration-200 ease-in-out',
                    isEnabled ? 'translate-x-5' : 'translate-x-0'
                  )}
                />
              </button>
            </motion.div>
          );
        })}
      </div>

      {/* Info Box */}
      <div className="flex items-start space-x-3 p-4 rounded-lg bg-neutral-blue-500/10 border border-neutral-blue-500/30">
        <Bell className="w-5 h-5 text-neutral-blue-400 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-charcoal-grey-300">
          <p className="font-medium mb-1">About Notifications</p>
          <p className="text-charcoal-grey-400">
            Notifications will appear in the application interface. You can view and manage them from the notification center.
          </p>
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

export { NotificationPreferencesPanel };
