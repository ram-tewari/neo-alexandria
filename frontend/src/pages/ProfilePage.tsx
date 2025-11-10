// Neo Alexandria 2.0 Frontend - Profile Page
// User profile and settings

import React from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { User } from 'lucide-react';

const ProfilePage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <User className="w-6 h-6 text-accent-blue-500" />
            <h1 className="text-2xl font-bold">Profile</h1>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-charcoal-grey-400">
            Profile and preferences coming soon...
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export { ProfilePage };
