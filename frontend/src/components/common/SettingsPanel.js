// frontend/src/components/common/SettingsPanel.js
import React, { useState } from 'react';
import { Key } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import ChangePassword from '../auth/ChangePassword';

const SettingsPanel = ({ 
  confidenceThreshold, 
  onConfidenceChange, 
  maxRecommendations, 
  onMaxRecommendationsChange 
}) => {
  const { user } = useAuth();
  const [showChangePassword, setShowChangePassword] = useState(false);

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
      {/* User Settings Section */}
      <div className="mb-6">
        <h3 className="font-semibold mb-4">User Settings</h3>
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <p className="text-sm font-medium text-gray-700">Account</p>
            <p className="text-sm text-gray-500">{user?.email}</p>
          </div>
          <button
            onClick={() => setShowChangePassword(!showChangePassword)}
            className="flex items-center space-x-2 bg-gray-600 hover:bg-gray-700 text-white px-3 py-1.5 rounded-lg transition-colors text-sm"
          >
            <Key className="w-4 h-4" />
            <span>Change Password</span>
          </button>
        </div>
        
        {showChangePassword && (
          <div className="mt-4">
            <ChangePassword onClose={() => setShowChangePassword(false)} />
          </div>
        )}
      </div>

      {/* Analysis Settings Section */}
      <div className="p-4 bg-gray-50 rounded-lg border">
        <h3 className="font-semibold mb-4">Analysis Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confidence Threshold: {confidenceThreshold}%
            </label>
            <input
              type="range"
              min="20"
              max="90"
              value={confidenceThreshold}
              onChange={(e) => onConfidenceChange(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>20% (More signals)</span>
              <span>90% (Fewer, stronger signals)</span>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Recommendations: {maxRecommendations}
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={maxRecommendations}
              onChange={(e) => onMaxRecommendationsChange(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>1</span>
              <span>10</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;