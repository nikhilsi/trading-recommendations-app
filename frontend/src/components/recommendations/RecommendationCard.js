import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { getActionColor, getRiskColor, calculatePotentialReturn } from '../../utils/helpers';

const RecommendationCard = ({ stock }) => {
  const getActionIcon = (action) => {
    return action === 'BUY' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />;
  };

  return (
    <div className="bg-gray-50 rounded-lg p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xl font-bold">{stock.symbol}</span>
            <span className={`flex items-center space-x-1 ${getActionColor(stock.action)} font-semibold`}>
              {getActionIcon(stock.action)}
              <span>{stock.action}</span>
            </span>
          </div>
          <p className="text-gray-600 text-sm">{stock.company || `${stock.symbol} Inc`}</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold">${stock.current_price || stock.price}</p>
          {stock.target_price && (
            <p className="text-sm text-gray-600">Target: ${stock.target_price}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-600">Potential Return</p>
          <p className="text-lg font-semibold text-green-600">
            +{calculatePotentialReturn(
              stock.current_price || stock.price, 
              stock.target_price, 
              stock.action
            ).toFixed(1)}%
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Confidence</p>
          <p className="text-lg font-semibold">{stock.confidence || 'N/A'}%</p>
        </div>
        {stock.timeframe && (
          <div>
            <p className="text-sm text-gray-600">Timeframe</p>
            <p className="text-sm font-medium">{stock.timeframe}</p>
          </div>
        )}
        {stock.risk_level && (
          <div>
            <p className="text-sm text-gray-600">Risk Level</p>
            <p className={`text-sm font-medium ${getRiskColor(stock.risk_level)}`}>
              {stock.risk_level}
            </p>
          </div>
        )}
      </div>

      {stock.reasoning && stock.reasoning.length > 0 && (
        <div className="border-t border-gray-200 pt-4">
          <h4 className="font-semibold mb-2 text-sm text-gray-700">Key Reasons:</h4>
          <ul className="space-y-1">
            {(Array.isArray(stock.reasoning) ? stock.reasoning.slice(0, 2) : [stock.reasoning]).map((reason, i) => (
              <li key={i} className="text-sm text-gray-600 flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default RecommendationCard;