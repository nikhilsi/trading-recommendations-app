// frontend/src/components/common/Header.js
import React from 'react';
import { Settings } from 'lucide-react';

const Header = ({ showSettings, onToggleSettings }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Stock Trading Intelligence</h1>
          <p className="text-gray-600 mt-1">
            Market Scanner & AI-Powered Recommendations
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={onToggleSettings}
            className="flex items-center space-x-2 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Header;