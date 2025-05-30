import { useState, useCallback } from 'react';
import { recommendationsApi } from '../services/api';

export const useRecommendations = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [confidenceThreshold, setConfidenceThreshold] = useState(50);
  const [maxRecommendations, setMaxRecommendations] = useState(5);

  const fetch = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        confidence_threshold: confidenceThreshold,
        max_recommendations: maxRecommendations
      };
      
      const response = await recommendationsApi.get(params);
      
      if (response.data && response.data.recommendations) {
        setData(response.data.recommendations);
      } else {
        setData(response.data || []);
      }
      
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError(`Failed to fetch recommendations: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [confidenceThreshold, maxRecommendations]);

  return {
    data,
    loading,
    error,
    lastUpdated,
    confidenceThreshold,
    setConfidenceThreshold,
    maxRecommendations,
    setMaxRecommendations,
    fetch
  };
};