import React from 'react';

const FilterPanel = ({ show, onToggle, filters, onFiltersChange }) => {
  return (
    <div className="mb-4">
      <button onClick={onToggle} className="text-sm text-blue-600 hover:text-blue-800 mb-3">
        {show ? '▼ Hide Advanced Filters' : '▶ Show Advanced Filters'} 
      </button>
      
      {show && (
        <div className="p-4 bg-gray-50 rounded-lg">
          {/* Price Filters */}
          <div className="mb-4">
            <h4 className="font-semibold text-sm mb-2">📊 Price</h4>
            <div className="grid grid-cols-2 gap-3">
              <input
                type="number"
                placeholder="Min Price"
                value={filters.minPrice || ''}
                onChange={(e) => onFiltersChange({...filters, minPrice: e.target.value})}
                className="px-3 py-2 border rounded"
              />
              <input
                type="number"
                placeholder="Max Price"
                value={filters.maxPrice || ''}
                onChange={(e) => onFiltersChange({...filters, maxPrice: e.target.value})}
                className="px-3 py-2 border rounded"
              />
            </div>
          </div>

          {/* Volume Filter */}
          <div className="mb-4">
            <h4 className="font-semibold text-sm mb-2">📈 Volume</h4>
            <select 
              value={filters.volumeFilter || 'any'}
              onChange={(e) => onFiltersChange({...filters, volumeFilter: e.target.value})}
              className="w-full px-3 py-2 border rounded"
            >
              <option value="any">Any Volume</option>
              <option value="1m">Above 1M</option>
              <option value="5m">Above 5M</option>
              <option value="10m">Above 10M</option>
              <option value="unusual">Unusual Volume (2x average)</option>
            </select>
          </div>

          {/* Change % Filter */}
          <div className="mb-4">
            <h4 className="font-semibold text-sm mb-2">📊 Price Change %</h4>
            <select 
              value={filters.changeFilter || 'any'}
              onChange={(e) => onFiltersChange({...filters, changeFilter: e.target.value})}
              className="w-full px-3 py-2 border rounded"
            >
              <option value="any">Any Change</option>
              <option value="up5">Up more than 5%</option>
              <option value="up2">Up more than 2%</option>
              <option value="down2">Down more than 2%</option>
              <option value="down5">Down more than 5%</option>
            </select>
          </div>

          {/* Technical Indicators */}
          <div className="mb-4">
            <h4 className="font-semibold text-sm mb-2">📉 Technical Indicators</h4>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.aboveSMA20 || false}
                  onChange={(e) => onFiltersChange({...filters, aboveSMA20: e.target.checked})}
                  className="mr-2"
                />
                <span className="text-sm">Price above 20-day SMA</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.aboveSMA50 || false}
                  onChange={(e) => onFiltersChange({...filters, aboveSMA50: e.target.checked})}
                  className="mr-2"
                />
                <span className="text-sm">Price above 50-day SMA</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.rsiOversold || false}
                  onChange={(e) => onFiltersChange({...filters, rsiOversold: e.target.checked})}
                  className="mr-2"
                />
                <span className="text-sm">RSI below 30 (Oversold)</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.rsiOverbought || false}
                  onChange={(e) => onFiltersChange({...filters, rsiOverbought: e.target.checked})}
                  className="mr-2"
                />
                <span className="text-sm">RSI above 70 (Overbought)</span>
              </label>
            </div>
          </div>

          {/* Pattern Recognition (Future) */}
          <div className="mb-4">
            <h4 className="font-semibold text-sm mb-2">🔍 Patterns (Coming Soon)</h4>
            <div className="text-sm text-gray-500">
              Triangle, Channel, Flag patterns will be available soon
            </div>
          </div>

          <button
            onClick={() => onFiltersChange({
              minPrice: 0,
              maxPrice: 0,
              volumeFilter: 'any',
              changeFilter: 'any',
              aboveSMA20: false,
              aboveSMA50: false,
              rsiOversold: false,
              rsiOverbought: false
            })}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Reset All Filters
          </button>
        </div>
      )}
    </div>
  );
};

export default FilterPanel;