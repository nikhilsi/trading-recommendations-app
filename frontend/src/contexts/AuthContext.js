// frontend/src/contexts/AuthContext.js
import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import axios from 'axios';

const AuthContext = createContext({});

// Configure axios defaults
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
axios.defaults.baseURL = API_BASE;

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tokens, setTokens] = useState(() => {
    // Load tokens from localStorage on init
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    return { accessToken, refreshToken };
  });

  // Save tokens to localStorage whenever they change
  useEffect(() => {
    if (tokens.accessToken) {
      localStorage.setItem('access_token', tokens.accessToken);
      localStorage.setItem('refresh_token', tokens.refreshToken);
      // Set default auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.accessToken}`;
    } else {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [tokens]);

  // Load user on mount if token exists
  useEffect(() => {
    if (tokens.accessToken) {
      loadUser();
    } else {
      setLoading(false);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const loadUser = async () => {
    try {
        // Ensure token is in header before making request
        if (tokens.accessToken) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.accessToken}`;
        }
        
        const response = await axios.get('/auth/me');
        setUser(response.data);
    } catch (error) {
        console.error('Failed to load user:', error);
        // Only logout if it's a 401 and we have a token
        if (error.response?.status === 401 && tokens.accessToken) {
        logout();
        }
    } finally {
        setLoading(false);
    }
};

  const login = async (email, password) => {
    try {
        const response = await axios.post('/auth/login', { email, password });
        const { access_token, refresh_token } = response.data;
        
        // Set tokens in state first
        setTokens({
        accessToken: access_token,
        refreshToken: refresh_token
        });
        
        // Immediately set the auth header
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        
        // Store in localStorage
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        
        // Wait a moment before loading user to ensure headers are set
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Now load user data
        await loadUser();
        
        return { success: true };
    } catch (error) {
        console.error('Login error:', error);
        return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
        };
    }
};

  const register = async (email, password, inviteCode) => {
    try {
      const response = await axios.post('/auth/register', {
        email,
        password,
        invite_code: inviteCode
      });
      
      const { access_token, refresh_token } = response.data;
      
      setTokens({
        accessToken: access_token,
        refreshToken: refresh_token
      });
      
      // Load user data
      await loadUser();
      
      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed'
      };
    }
  };

  const logout = useCallback(() => {
    // Call logout endpoint (optional, clears server sessions)
    try {
      axios.post('/auth/logout').catch(() => {});
    } catch (error) {
      // Ignore errors
    }
    
    // Clear local state
    setTokens({ accessToken: null, refreshToken: null });
    setUser(null);
  }, []);

  const refreshAccessToken = async () => {
    try {
      if (!tokens.refreshToken) {
        throw new Error('No refresh token');
      }
      
      const response = await axios.post('/auth/refresh', {
        refresh_token: tokens.refreshToken
      });
      
      const { access_token, refresh_token } = response.data;
      
      setTokens({
        accessToken: access_token,
        refreshToken: refresh_token
      });
      
      return access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
      return null;
    }
  };

  // Set up axios interceptor for token refresh
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          const newToken = await refreshAccessToken();
          if (newToken) {
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
            return axios(originalRequest);
          }
        }
        
        return Promise.reject(error);
      }
    );
    
    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, [tokens.refreshToken]); // eslint-disable-line react-hooks/exhaustive-deps

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refreshAccessToken
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
