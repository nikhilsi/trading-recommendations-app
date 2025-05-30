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
    minScore: 30,
    volumeFilter: 'any',
    changeFilter: 'any',
    aboveSMA20: false,
    aboveSMA50: false,
    rsiOversold: false,
    rsiOverbought: false
  });

  // Check if any filters are active
  const hasActiveFilters = filters.minPrice > 0 || 
                          filters.maxPrice > 0 || 
                          filters.volumeFilter !== 'any' ||
                          filters.changeFilter !== 'any' ||
                          filters.aboveSMA20 ||
                          filters.aboveSMA50 ||
                          filters.rsiOversold ||
                          filters.rsiOverbought;

  const handleScan = async () => {
    // Validate "ALL" requires filters
    if (scanType === 'all' && !hasActiveFilters) {
      alert('Please apply at least one filter when screening all stocks. This helps narrow down 8000+ stocks to meaningful results.');
      setShowFilters(true);  // Open filter panel
      return;
    }
    
    // Close filters when scanning
    setShowFilters(false);
    
    if (hasActiveFilters) {
      const filterData = {
        min_price: filters.minPrice || 0,
        max_price: filters.maxPrice || 0,
        volume_filter: filters.volumeFilter || 'any',
        change_filter: filters.changeFilter || 'any',
        above_sma_20: filters.aboveSMA20 || false,
        above_sma_50: filters.aboveSMA50 || false,
        rsi_oversold: filters.rsiOversold || false,
        rsi_overbought: filters.rsiOverbought || false,
        scan_type: scanType  // Include scan type in filters
      };
      
      console.log('Applying filters:', filterData);
      onScan(filterData, true);  // Pass true to indicate screener mode
    } else {
      onScan({}, false);  // Regular scan without filters
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
      <h3 className="text-lg font-semibold mb-4">
        🔍 Market {hasActiveFilters ? 'Screener' : 'Scanner'}
      </h3>
      
      <ScanControls
        scanType={scanType}
        onScanTypeChange={setScanType}
        onScan={handleScan}
        loading={loading}
        lastScanTime={lastScanTime}
        hasActiveFilters={hasActiveFilters}
      />
      
      {/* Warning for ALL mode without filters */}
      {scanType === 'all' && !showFilters && !hasActiveFilters && (
        <div className="bg-amber-50 border border-amber-200 rounded p-3 mb-3 text-sm">
          <p className="text-amber-800">
            ⚠️ <strong>All Stocks</strong> mode screens 8000+ stocks. 
            Please apply filters to get meaningful results.
          </p>
        </div>
      )}
      
      <FilterPanel
        show={showFilters}
        onToggle={() => setShowFilters(!showFilters)}
        filters={filters}
        onFiltersChange={setFilters}
      />

      {/* Show indicator when filters are active but panel is closed */}
      {hasActiveFilters && !showFilters && (
        <div className="mb-2 text-sm text-blue-600">
          ✓ Filters active - {marketStats?.total_matched || 0} matches from {marketStats?.total_symbols_scanned || 0} stocks
        </div>
      )}

      {marketStats && marketStats.total_symbols_scanned > 0 && !hasActiveFilters && (
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
            <p className="text-gray-500">
              Click "{hasActiveFilters ? 'Screen' : 'Scan'} Market" to find opportunities
            </p>
            <p className="text-sm text-gray-400 mt-1">Powered by Polygon.io & Yahoo Finance</p>
          </div>
        )
      )}
    </div>
  );
};

export default MarketScanner;