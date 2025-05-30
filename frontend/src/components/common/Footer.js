import React from 'react';
import { AlertCircle } from 'lucide-react';

const Footer = () => {
  return (
    <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <div className="flex items-start space-x-2">
        <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
        <div>
          <p className="text-sm text-yellow-800">
            <strong>Disclaimer:</strong> These recommendations are for educational purposes only. 
            Trading involves substantial risk and may not be suitable for all investors. 
            Always conduct your own research and consider your risk tolerance.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Footer;