import React from 'react';
import { RefreshCw } from 'lucide-react';

const LoadingSpinner = ({ message = "Loading..." }) => {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="text-center">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-600 mb-4" />
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  );
};

export default LoadingSpinner;