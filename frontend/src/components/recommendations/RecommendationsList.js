import React from 'react';
import { RefreshCw } from 'lucide-react';
import RecommendationCard from './RecommendationCard';
import EmptyState from './EmptyState';

const RecommendationsList = ({ 
  recommendations, 
  loading, 
  onRefresh, 
  lastUpdated,
  confidenceThreshold,
  maxRecommendations,
  watchlistSize
}) => {
  const showInitialState = !loading && recommendations.length === 0 && !lastUpdated;

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">🤖 AI Recommendations</h3>
        <button 
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Analyze Watchlist</span>
        </button>
      </div>

      {lastUpdated && (
        <p className="text-sm text-gray-500 mb-4">
          Last analysis: {lastUpdated.toLocaleTimeString()} • Confidence ≥{confidenceThreshold}% • Max {maxRecommendations} stocks
        </p>
      )}

      {showInitialState ? (
        <EmptyState 
          type="initial"
          confidenceThreshold={confidenceThreshold}
          watchlistSize={watchlistSize}
        />
      ) : recommendations.length === 0 ? (
        <EmptyState 
          type="no-signals"
          confidenceThreshold={confidenceThreshold}
          watchlistSize={watchlistSize}
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {recommendations.map((stock, index) => (
            <RecommendationCard key={`${stock.symbol}-${index}`} stock={stock} />
          ))}
        </div>
      )}
    </div>
  );
};

export default RecommendationsList;