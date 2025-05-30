import React from 'react';

const OpportunityCard = ({ opportunity, onAddToWatchlist, isInWatchlist }) => {
  return (
    <div className="border rounded-lg p-3 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div>
          <span className="font-bold text-lg">{opportunity.symbol}</span>
          <p className="text-sm text-gray-600">Score: {opportunity.score}</p>
          <span className={`text-xs px-2 py-0.5 rounded-full ${
            opportunity.data_source === 'polygon' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'
          }`}>
            {opportunity.data_source === 'polygon' ? '🔷 Polygon' : '📊 Yahoo'}
          </span>
        </div>
        <div className="text-right">
          <p className="font-semibold">${opportunity.price}</p>
          <p className={`text-sm ${opportunity.change_percent > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {opportunity.change_percent > 0 ? '+' : ''}{opportunity.change_percent}%
          </p>
        </div>
      </div>
      <div className="mt-2">
        {opportunity.signals && opportunity.signals.map((signal, i) => (
          <p key={i} className="text-xs text-gray-700">• {signal}</p>
        ))}
      </div>
      <div className="mt-2 flex justify-between">
        <button
          onClick={() => onAddToWatchlist(opportunity.symbol)}
          className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
          disabled={isInWatchlist}
        >
          {isInWatchlist ? 'In Watchlist' : 'Add to Watchlist'}
        </button>
      </div>
    </div>
  );
};

export default OpportunityCard;