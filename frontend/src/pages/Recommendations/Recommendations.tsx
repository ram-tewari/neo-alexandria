import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { RecommendationFeed } from '@/components/recommendation/RecommendationFeed';
import { UserProfile } from '@/components/recommendation/UserProfile';
import { Modal } from '@/components/common/Modal';

export const Recommendations: React.FC = () => {
  const navigate = useNavigate();
  const [showPreferences, setShowPreferences] = useState(false);

  const handleResourceClick = (resourceId: string) => {
    navigate(`/resources/${resourceId}`);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <RecommendationFeed
        onResourceClick={handleResourceClick}
        onPreferencesClick={() => setShowPreferences(true)}
      />

      <Modal
        isOpen={showPreferences}
        onClose={() => setShowPreferences(false)}
        title="Recommendation Preferences"
      >
        <UserProfile onClose={() => setShowPreferences(false)} />
      </Modal>
    </div>
  );
};
