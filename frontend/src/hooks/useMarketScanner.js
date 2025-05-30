// frontend/src/hooks/useMarketScanner.js
import { useState, useCallback } from 'react';
import { marketApi } from '../services/api';

export const useMarketScanner = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [scanType, setScanType] = useState('momentum');
  const [loading, setLoading] = useState(false);
  const [lastScanTime, setLastScanTime] = useState(null);
  const [marketStats, setMarketStats] = useState(null);
  const [error, setError] = useState(null);

  const scan = useCallback(async (filters = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        scan_type: scanType,
        limit: 15,
        source: 'polygon',
        ...filters
      };
      
      const response = await marketApi.scan(params);
      
      if (response.data && response.data.opportunities) {
        setOpportunities(response.data.opportunities);
        setLastScanTime(new Date());
        
        if (response.data.market_stats) {
          setMarketStats(response.data.market_stats);
        }
      }
    } catch (err) {
      console.error('Market scan error:', err);
      setError(`Failed to scan market: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [scanType]);

  return {
    opportunities,
    scanType,
    setScanType,
    loading,
    lastScanTime,
    marketStats,
    error,
    scan
  };
};