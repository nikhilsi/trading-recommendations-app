import React from 'react';
import { Activity, RefreshCw } from 'lucide-react';

const ScanControls = ({ 
  scanType, 
  onScanTypeChange, 
  onScan, 
  loading, 
  lastScanTime,
  hasActiveFilters  // Add this prop
}) => {
  return (
    <div className="flex items-center space-x-4 mb-4">
      <select
        value={scanType}
        onChange={(e) => onScanTypeChange(e.target.value)}
        className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="momentum">🚀 Momentum Gainers</option>
        <option value="volume">📊 Volume Movers</option>
        <option value="oversold">📉 Oversold Bounce</option>
        <option value="most_active">🔥 Most Active</option>
        <option value="all">🌐 All Stocks (Requires Filters)</option>
      </select>
      
      <button
        onClick={onScan}
        disabled={loading}
        className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-lg transition-colors"
      >
        {loading ? (
          <RefreshCw className="w-4 h-4 animate-spin" />
        ) : (
          <Activity className="w-4 h-4" />
        )}
        <span>
          {loading ? 'Screening...' : hasActiveFilters ? 'Screen Market' : 'Scan Market'}
        </span>
      </button>
      
      {lastScanTime && (
        <span className="text-sm text-gray-500">
          Last {hasActiveFilters ? 'screen' : 'scan'}: {lastScanTime.toLocaleTimeString()}
        </span>
      )}
    </div>
  );
};

export default ScanControls;