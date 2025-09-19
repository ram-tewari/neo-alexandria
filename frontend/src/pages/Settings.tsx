// Neo Alexandria 2.0 Frontend - Settings Page
// Application configuration and user preferences

import React from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Settings as SettingsIcon, Palette, Database, Shield } from 'lucide-react';

const Settings: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-secondary-900 mb-2">Settings</h1>
        <p className="text-secondary-600">
          Configure your Neo Alexandria experience
        </p>
      </div>

      {/* Coming Soon */}
      <Card>
        <CardContent className="text-center py-12">
          <div className="text-secondary-400 mb-6">
            <SettingsIcon className="w-16 h-16 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-secondary-900 mb-2">
              Settings Panel Coming Soon
            </h3>
            <p className="text-secondary-600 max-w-sm mx-auto mb-6">
              Customize your experience with themes, API settings, and more.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
            <div className="text-center p-4 border border-secondary-200 rounded-lg">
              <Palette className="w-8 h-8 mx-auto mb-2 text-purple-500" />
              <h4 className="font-medium mb-1">Appearance</h4>
              <p className="text-sm text-secondary-600">Themes, layout preferences</p>
            </div>
            
            <div className="text-center p-4 border border-secondary-200 rounded-lg">
              <Database className="w-8 h-8 mx-auto mb-2 text-blue-500" />
              <h4 className="font-medium mb-1">API Configuration</h4>
              <p className="text-sm text-secondary-600">Server settings and endpoints</p>
            </div>
            
            <div className="text-center p-4 border border-secondary-200 rounded-lg">
              <Shield className="w-8 h-8 mx-auto mb-2 text-green-500" />
              <h4 className="font-medium mb-1">Privacy & Security</h4>
              <p className="text-sm text-secondary-600">Data handling preferences</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export { Settings };
