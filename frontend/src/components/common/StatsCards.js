import React from 'react';
import { Activity, TrendingUp, TrendingDown, Database } from 'lucide-react';

const StatsCards = ({ 
  marketOpportunities, 
  recommendations, 
  buySignals, 
  sellSignals, 
  watchlistSize 
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
      <div className="bg-white p-4 rounded-lg shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-600 text-sm">Market Opportunities</p>
            <p className="text-2xl font-bold">{marketOpportunities}</p>
          </div>
          <Activity className="w-6 h-6 text-purple-600" />
        </div>
      </div>
      
      <div className="bg-white p-4 rounded-lg shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-600 text-sm">AI Recommendations</p>
            <p className="text-2xl font-bold">{recommendations}</p>
          </div>
          <TrendingUp className="w-6 h-6 text-blue-600" />
        </div>
      </div>
      
      <div className="bg-white p-4 rounded-lg shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-600 text-sm">Buy Signals</p>
            <p className="text-2xl font-bold text-green-600">{buySignals}</p>
          </div>
          <TrendingUp className="w-6 h-6 text-green-600" />
        </div>
      </div>
      
      <div className="bg-white p-4 rounded-lg shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-600 text-sm">Sell Signals</p>
            <p className="text-2xl font-bold text-red-600">{sellSignals}</p>
          </div>
          <TrendingDown className="w-6 h-6 text-red-600" />
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-600 text-sm">Watchlist Size</p>
            <p className="text-2xl font-bold">{watchlistSize}</p>
          </div>
          <Database className="w-6 h-6 text-purple-600" />
        </div>
      </div>
    </div>
  );
};

export default StatsCards;