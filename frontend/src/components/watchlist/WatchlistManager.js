import React, { useState } from 'react';
import { Plus, X } from 'lucide-react';

const WatchlistManager = ({ watchlist, onAdd, onRemove, dbStats }) => {
  const [newSymbol, setNewSymbol] = useState('');

  const handleAdd = () => {
    if (newSymbol.trim()) {
      onAdd(newSymbol);
      setNewSymbol('');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
      <h3 className="text-lg font-semibold mb-4">📋 Watchlist Management</h3>
      
      <div className="flex items-center space-x-2 mb-4">
        <input
          type="text"
          placeholder="Enter symbol (e.g., AAPL)"
          value={newSymbol}
          onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
          onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleAdd}
          className="flex items-center space-x-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add</span>
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        {watchlist.map((symbol) => (
          <div key={symbol} className="flex items-center space-x-1 bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
            <span className="font-medium">{symbol}</span>
            <button
              onClick={() => onRemove(symbol)}
              className="text-blue-600 hover:text-blue-800"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        ))}
      </div>

      {dbStats && (
        <div className="mt-4 text-sm text-gray-600">
          Database: {dbStats.total_stocks} stocks • {dbStats.total_recommendations} historical recommendations • {dbStats.total_prices} price records
        </div>
      )}
    </div>
  );
};

export default WatchlistManager;