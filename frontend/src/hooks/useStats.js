import { useState, useCallback } from 'react';
import { statsApi } from '../services/api';

export const useStats = () => {
  const [data, setData] = useState(null);
  const [loading] = useState(false);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    try {
      const response = await statsApi.get();
      setData(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError(err.message);
    }
  }, []); // Empty deps - function never changes

  return {
    data,
    loading,
    error,
    fetch
  };
};