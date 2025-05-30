// frontend/src/components/market-scanner/MarketScanner.js
import React, { useState } from 'react';
import { Activity } from 'lucide-react';
import ScanControls from './ScanControls';
import FilterPanel from './FilterPanel';
import OpportunityCard from './OpportunityCard';

const MarketScanner = ({ 
  opportunities, 
  scanType, 
  setScanType, 
  loading, 
  lastScanTime,
  marketStats,
  onScan,
  onAddToWatchlist,
  watchlist 
}) => {
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    minPrice: 0,
    maxPrice: 0,
    minVolume: 0,
    minScore: 30
  });

  const handleScan = () => {
    onScan(filters);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
      <h3 className="text-lg font-semibold mb-4">🔍 Market Scanner</h3>
      
      <ScanControls
        scanType={scanType}
        onScanTypeChange={setScanType}
        onScan={handleScan}
        loading={loading}
        lastScanTime={lastScanTime}
      />
      
      <FilterPanel
        show={showFilters}
        onToggle={() => setShowFilters(!showFilters)}
        filters={filters}
        onFiltersChange={setFilters}
      />

      {marketStats && marketStats.total_symbols_scanned > 0 && (
        <div className="mt-2 text-sm text-gray-600">
          Scanned {marketStats.total_symbols_scanned.toLocaleString()} stocks across entire market
        </div>
      )}

      {opportunities.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {opportunities.slice(0, 9).map((opp, index) => (
            <OpportunityCard
              key={`${opp.symbol}-${index}`}
              opportunity={opp}
              onAddToWatchlist={onAddToWatchlist}
              isInWatchlist={watchlist.includes(opp.symbol)}
            />
          ))}
        </div>
      ) : (
        !loading && (
          <div className="text-center py-8">
            <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">Click "Scan Market" to find opportunities</p>
            <p className="text-sm text-gray-400 mt-1">Powered by Polygon.io & Yahoo Finance</p>
          </div>
        )
      )}
    </div>
  );
};

export default MarketScanner;