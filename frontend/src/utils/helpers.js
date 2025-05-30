// frontend/src/utils/helpers.js
export const getActionColor = (action) => {
  return action === 'BUY' ? 'text-green-600' : 'text-red-600';
};

export const getActionIcon = (action) => {
  return action === 'BUY' ? 'TrendingUp' : 'TrendingDown';
};

export const getRiskColor = (risk) => {
  if (risk && risk.includes('High')) return 'text-red-500';
  if (risk && risk.includes('Medium')) return 'text-yellow-500';
  return 'text-green-500';
};

export const calculatePotentialReturn = (current, target, action) => {
  if (!current || !target) return 0;
  if (action === 'BUY') {
    return ((target - current) / current * 100);
  } else {
    return ((current - target) / current * 100);
  }
};