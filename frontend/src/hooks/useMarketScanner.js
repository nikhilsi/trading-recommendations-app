// frontend/src/hooks/useMarketScanner.js
import { useState, useCallback } from 'react';
import { marketApi } from '../services/api';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const useMarketScanner = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [scanType, setScanType] = useState('momentum');
  const [loading, setLoading] = useState(false);
  const [lastScanTime, setLastScanTime] = useState(null);
  const [marketStats, setMarketStats] = useState(null);
  const [error, setError] = useState(null);

  const scan = useCallback(async (filters = {}, useScreener = false) => {
    try {
      setLoading(true);
      setError(null);
      
      let response;
      
      if (useScreener && Object.keys(filters).length > 0) {
        // Use screener endpoint for filtered searches
        console.log('Using screener with filters:', filters);
        response = await axios.post(`${API_BASE}/api/market/screen`, filters);
      } else {
        // Use regular scan endpoint
        const params = {
          scan_type: scanType,
          limit: 15,
          source: 'polygon'
        };
        response = await marketApi.scan(params);
      }
      
      if (response.data) {

        // Debug: Log the entire response
        console.log('Full response data:', response.data);

        // Handle both response formats
        const opportunities = response.data.opportunities || response.data.results || [];
        setOpportunities(opportunities);
        setLastScanTime(new Date());
        
        // Handle market stats from both scanner and screener
        if (response.data.market_stats || response.data.total_screened || response.data.total_matched) {
          setMarketStats({
            total_symbols_scanned: response.data.total_screened || 
                                 response.data.market_stats?.total_symbols_scanned || 
                                 0,
            total_matched: response.data.total_matched || 
                          opportunities.length,
            pre_filter_count: response.data.market_stats?.pre_filter_count,
            post_filter_count: response.data.market_stats?.post_filter_count
          });

          // Debug: Log what we set
          console.log('Market stats set to:', {
            total_symbols_scanned: response.data.total_screened || response.data.market_stats?.total_symbols_scanned || 0,
            total_matched: response.data.total_matched || opportunities.length
  });
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