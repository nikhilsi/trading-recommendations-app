import React from 'react';
import { Activity } from 'lucide-react';

const EmptyState = ({ type, confidenceThreshold, watchlistSize }) => {
  if (type === 'initial') {
    return (
      <div className="text-center py-8">
        <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Ready to Analyze</h3>
        <p className="text-gray-600">
          Click "Analyze Watchlist" to generate AI-powered recommendations.
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Current settings: {confidenceThreshold}% confidence • {watchlistSize} stocks in watchlist
        </p>
      </div>
    );
  }

  return (
    <div className="text-center py-8">
      <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 className="text-lg font-semibold text-gray-900 mb-2">No Strong Signals Found</h3>
      <p className="text-gray-600">
        Try lowering the confidence threshold or check back later for new opportunities.
      </p>
      <p className="text-sm text-gray-500 mt-2">
        Current threshold: {confidenceThreshold}% • Analyzed {watchlistSize} stocks
      </p>
    </div>
  );
};

export default EmptyState;