import React from 'react';

const SettingsPanel = ({ 
  confidenceThreshold, 
  onConfidenceChange, 
  maxRecommendations, 
  onMaxRecommendationsChange 
}) => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
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