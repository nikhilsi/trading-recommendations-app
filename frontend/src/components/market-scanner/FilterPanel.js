import React from 'react';

const FilterPanel = ({ show, onToggle, filters, onFiltersChange }) => {
  const handleFilterChange = (key, value) => {
    onFiltersChange({
      ...filters,
      [key]: value
    });
  };

  return (
    <div className="mb-4">
      <button
        onClick={onToggle}
        className="text-sm text-blue-600 hover:text-blue-800"
      >
        {show ? '▼ Hide Filters' : '▶ Show Filters'} 
      </button>
      
      {show && (
        <div className="mt-3 p-4 bg-gray-50 rounded-lg grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs text-gray-600 mb-1">Min Price ($)</label>
            <input
              type="number"
              value={filters.minPrice}
              onChange={(e) => handleFilterChange('minPrice', parseFloat(e.target.value) || 0)}
              className="w-full px-2 py-1 border rounded text-sm"
              placeholder="0"
            />
          </div>
          
          <div>
            <label className="block text-xs text-gray-600 mb-1">Max Price ($)</label>
            <input
              type="number"
              value={filters.maxPrice}
              onChange={(e) => handleFilterChange('maxPrice', parseFloat(e.target.value) || 0)}
              className="w-full px-2 py-1 border rounded text-sm"
              placeholder="No limit"
            />
          </div>
          
          <div>
            <label className="block text-xs text-gray-600 mb-1">Min Volume</label>
            <input
              type="number"
              value={filters.minVolume}
              onChange={(e) => handleFilterChange('minVolume', parseInt(e.target.value) || 0)}
              className="w-full px-2 py-1 border rounded text-sm"
              placeholder="0"
            />
          </div>
          
          <div>
            <label className="block text-xs text-gray-600 mb-1">Min Score</label>
            <input
              type="number"
              value={filters.minScore}
              onChange={(e) => handleFilterChange('minScore', parseInt(e.target.value) || 0)}
              className="w-full px-2 py-1 border rounded text-sm"
              min="0"
              max="100"
            />
          </div>
          
          <div className="col-span-2 md:col-span-4">
            <button
              onClick={() => onFiltersChange({minPrice: 0, maxPrice: 0, minVolume: 0, minScore: 30})}
              className="text-xs text-gray-500 hover:text-gray-700"
            >
              Reset Filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterPanel;