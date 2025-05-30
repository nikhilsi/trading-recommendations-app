import { useState, useCallback } from 'react';
import { watchlistApi } from '../services/api';

export const useWatchlist = () => {
  const [symbols, setSymbols] = useState([]);
  const [loading] = useState(false);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    try {
      const response = await watchlistApi.get();
      setSymbols(response.data.watchlist || []);
    } catch (err) {
      console.error('Error fetching watchlist:', err);
      setError(err.message);
    }
  }, []);

  const add = useCallback(async (symbol) => {
    if (!symbol) return;
    
    try {
      await watchlistApi.add(symbol.toUpperCase());
      await fetch(); // Refresh the list
    } catch (err) {
      console.error('Error adding symbol:', err);
      setError(`Failed to add ${symbol}: ${err.response?.data?.detail || err.message}`);
    }
  }, [fetch]);

  const remove = useCallback(async (symbol) => {
    try {
      await watchlistApi.remove(symbol);
      await fetch(); // Refresh the list
    } catch (err) {
      console.error('Error removing symbol:', err);
      setError(err.message);
    }
  }, [fetch]);

  return {
    symbols,
    loading,
    error,
    fetch,
    add,
    remove
  };
};