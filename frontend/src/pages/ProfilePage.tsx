// Neo Alexandria 2.0 Frontend - Profile Page
// User profile and settings with tabbed interface

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { User, Settings, Bell, Palette } from 'lucide-react';
import { useAppStore } from '@/store';
import { cn } from '@/utils/cn';
import { PreferencesPanel } from '@/components/profile/PreferencesPanel';
import { AccountSettingsPanel } from '@/components/profile/AccountSettingsPanel';
import { NotificationPreferencesPanel } from '@/components/profile/NotificationPreferencesPanel';

type TabId = 'preferences' | 'account' | 'notifications';

interface Tab {
  id: TabId;
  label: string;
  icon: React.ReactNode;
}

const tabs: Tab[] = [
  { id: 'preferences', label: 'Preferences', icon: <Palette className="w-4 h-4" /> },
  { id: 'account', label: 'Account Settings', icon: <Settings className="w-4 h-4" /> },
  { id: 'notifications', label: 'Notifications', icon: <Bell className="w-4 h-4" /> },
];

const ProfilePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabId>('preferences');
  const preferences = useAppStore((state) => state.preferences);

  // Animation variants for tab content
  const contentVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { duration: 0.2 }
    },
    exit: { 
      opacity: 0, 
      x: 20,
      transition: { duration: 0.15 }
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'preferences':
        return <PreferencesPanel />;
      case 'account':
        return <AccountSettingsPanel />;
      case 'notifications':
        return <NotificationPreferencesPanel />;
      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <User className="w-8 h-8 text-accent-blue-500" />
          <h1 className="text-3xl font-bold text-charcoal-grey-50">Profile & Settings</h1>
        </div>
        <p className="text-charcoal-grey-400">
          Manage your preferences, account settings, and notifications
        </p>
      </div>

      <Card padding="none" variant="glass">
        {/* Tab Navigation */}
        <div className="border-b border-charcoal-grey-700">
          <nav className="flex space-x-1 px-6" aria-label="Profile tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  'relative flex items-center space-x-2 px-4 py-4 text-sm font-medium transition-colors duration-200',
                  'focus:outline-none focus:ring-2 focus:ring-accent-blue-500 focus:ring-offset-2 focus:ring-offset-charcoal-grey-900',
                  activeTab === tab.id
                    ? 'text-accent-blue-400'
                    : 'text-charcoal-grey-400 hover:text-charcoal-grey-200'
                )}
                aria-current={activeTab === tab.id ? 'page' : undefined}
              >
                {tab.icon}
                <span>{tab.label}</span>
                
                {/* Active tab indicator */}
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent-blue-500"
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  />
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              variants={contentVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
            >
              {renderTabContent()}
            </motion.div>
          </AnimatePresence>
        </div>
      </Card>
    </div>
  );
};

export { ProfilePage };
