import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, Activity, RefreshCw, AlertCircle, Settings, Plus, X, Database } from 'lucide-react';
import './App.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  
  // Dynamic controls
  const [confidenceThreshold, setConfidenceThreshold] = useState(50);
  const [maxRecommendations, setMaxRecommendations] = useState(5);
  const [showSettings, setShowSettings] = useState(false);
  const [newSymbol, setNewSymbol] = useState('');
  
  // Persistence stats
  const [dbStats, setDbStats] = useState(null);

  // Market scanner state
  const [marketOpportunities, setMarketOpportunities] = useState([]);
  const [scanType, setScanType] = useState('momentum');
  const [scanLoading, setScanLoading] = useState(false);
  const [lastScanTime, setLastScanTime] = useState(null);
  const [marketStats, setMarketStats] = useState(null);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        confidence_threshold: confidenceThreshold,
        max_recommendations: maxRecommendations
      });
      
      console.log('Fetching from:', `${API_BASE}/api/recommendations?${params}`);
      const response = await axios.get(`${API_BASE}/api/recommendations?${params}`);
      
      if (response.data && response.data.recommendations) {
        setRecommendations(response.data.recommendations);
      } else {
        setRecommendations(response.data || []);
      }
      
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError(`Failed to fetch recommendations: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const scanMarket = async () => {
    try {
      setScanLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE}/api/market/scan?scan_type=${scanType}&limit=15&source=polygon`);
      
      console.log('Scanner response:', response.data);
      
      if (response.data && response.data.opportunities) {
        setMarketOpportunities(response.data.opportunities);
        setLastScanTime(new Date());
        
        // Capture market stats
        if (response.data.market_stats) {
          setMarketStats(response.data.market_stats);
        }
      }
    } catch (err) {
      console.error('Market scan error:', err);
      setError(`Failed to scan market: ${err.message}`);
    } finally {
      setScanLoading(false);
    }
  };

  const fetchWatchlist = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/watchlist`);
      setWatchlist(response.data.watchlist || []);
    } catch (err) {
      console.error('Error fetching watchlist:', err);
    }
  };

  const fetchDbStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/stats`);
      setDbStats(response.data);
    } catch (err) {
      console.error('Error fetching DB stats:', err);
    }
  };

  const addToWatchlist = async (symbolToAdd = null) => {
    const symbol = symbolToAdd || newSymbol.trim();
    if (!symbol) return;
    
    try {
      await axios.post(`${API_BASE}/api/watchlist`, {
        symbol: symbol.toUpperCase()
      });
      setNewSymbol('');
      fetchWatchlist();
    } catch (err) {
      console.error('Error adding symbol:', err);
      setError(`Failed to add ${symbol}: ${err.response?.data?.detail || err.message}`);
    }
  };

  const removeFromWatchlist = async (symbol) => {
    try {
      await axios.delete(`${API_BASE}/api/watchlist/${symbol}`);
      fetchWatchlist();
    } catch (err) {
      console.error('Error removing symbol:', err);
    }
  };

  useEffect(() => {
    fetchWatchlist();
    fetchDbStats();
  }, []);

  const getActionColor = (action) => {
    return action === 'BUY' ? 'text-green-600' : 'text-red-600';
  };

  const getActionIcon = (action) => {
    return action === 'BUY' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />;
  };

  const getRiskColor = (risk) => {
    if (risk && risk.includes('High')) return 'text-red-500';
    if (risk && risk.includes('Medium')) return 'text-yellow-500';
    return 'text-green-500';
  };

  const calculatePotentialReturn = (current, target, action) => {
    if (!current || !target) return 0;
    if (action === 'BUY') {
      return ((target - current) / current * 100);
    } else {
      return ((current - target) / current * 100);
    }
  };

  useEffect(() => {
    fetchDbStats();
  }, [confidenceThreshold, maxRecommendations]);

  const showInitialState = !loading && recommendations.length === 0 && !lastUpdated;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-600 mb-4" />
          <p className="text-gray-600">Analyzing market data...</p>
          <p className="text-sm text-gray-500">Confidence threshold: {confidenceThreshold}%</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Stock Trading Intelligence</h1>
              <p className="text-gray-600 mt-1">
                Market Scanner & AI-Powered Recommendations
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <button 
                onClick={() => setShowSettings(!showSettings)}
                className="flex items-center space-x-2 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </button>
            </div>
          </div>

          {/* Settings Panel */}
          {showSettings && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg border">
              <h3 className="font-semibold mb-4">Analysis Settings</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Confidence Threshold: {confidenceThreshold}%
                  </label>
                  <input
                    type="range"
                    min="20"
                    max="90"
                    value={confidenceThreshold}
                    onChange={(e) => setConfidenceThreshold(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>20% (More signals)</span>
                    <span>90% (Fewer, stronger signals)</span>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Recommendations: {maxRecommendations}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={maxRecommendations}
                    onChange={(e) => setMaxRecommendations(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>1</span>
                    <span>10</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Market Scanner Section - PRIMARY FEATURE */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">🔍 Market Scanner</h3>
          
          <div className="flex items-center space-x-4 mb-4">
            <select
              value={scanType}
              onChange={(e) => setScanType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="momentum">🚀 Momentum Gainers</option>
              <option value="volume">📊 Volume Movers</option>
              <option value="oversold">📉 Oversold Bounce</option>
              <option value="most_active">🔥 Most Active</option>
            </select>
            
            <button
              onClick={scanMarket}
              disabled={scanLoading}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-lg transition-colors"
            >
              {scanLoading ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Activity className="w-4 h-4" />
              )}
              <span>{scanLoading ? 'Scanning...' : 'Scan Market'}</span>
            </button>
            
            {lastScanTime && (
              <span className="text-sm text-gray-500">
                Last scan: {lastScanTime.toLocaleTimeString()}
              </span>
            )}
          </div>
          
          {marketStats && marketStats.total_symbols_scanned > 0 && (
            <div className="mt-2 text-sm text-gray-600">
              Scanned {marketStats.total_symbols_scanned.toLocaleString()} stocks across entire market
            </div>
          )}
          
          {/* Display scan results */}
          {marketOpportunities.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {marketOpportunities.slice(0, 9).map((opp, index) => (
                <div key={`${opp.symbol}-${index}`} className="border rounded-lg p-3 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="font-bold text-lg">{opp.symbol}</span>
                      <p className="text-sm text-gray-600">Score: {opp.score}</p>
                      {/* Add data source badge */}
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        opp.data_source === 'polygon' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'
                      }`}>
                        {opp.data_source === 'polygon' ? '🔷 Polygon' : '📊 Yahoo'}
                      </span>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">${opp.price}</p>
                      <p className={`text-sm ${opp.change_percent > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {opp.change_percent > 0 ? '+' : ''}{opp.change_percent}%
                      </p>
                    </div>
                  </div>
                  <div className="mt-2">
                    {opp.signals && opp.signals.map((signal, i) => (
                      <p key={i} className="text-xs text-gray-700">• {signal}</p>
                    ))}
                  </div>
                  <div className="mt-2 flex justify-between">
                    <button
                      onClick={() => addToWatchlist(opp.symbol)}
                      className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
                      disabled={watchlist.includes(opp.symbol)}
                    >
                      {watchlist.includes(opp.symbol) ? 'In Watchlist' : 'Add to Watchlist'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {marketOpportunities.length === 0 && !scanLoading && (
            <div className="text-center py-8">
              <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Click "Scan Market" to find opportunities</p>
              <p className="text-sm text-gray-400 mt-1">Yahoo Finance powered scanner</p>
            </div>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Market Opportunities</p>
                <p className="text-2xl font-bold">{marketOpportunities.length}</p>
              </div>
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">AI Recommendations</p>
                <p className="text-2xl font-bold">{recommendations.length}</p>
              </div>
              <TrendingUp className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Buy Signals</p>
                <p className="text-2xl font-bold text-green-600">
                  {recommendations.filter(r => r.action === 'BUY').length}
                </p>
              </div>
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Sell Signals</p>
                <p className="text-2xl font-bold text-red-600">
                  {recommendations.filter(r => r.action === 'SELL').length}
                </p>
              </div>
              <TrendingDown className="w-6 h-6 text-red-600" />
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Watchlist Size</p>
                <p className="text-2xl font-bold">{watchlist.length}</p>
              </div>
              <Database className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        {/* AI Recommendations Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">🤖 AI Recommendations</h3>
            <button 
              onClick={fetchRecommendations}
              disabled={loading}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Analyze Watchlist</span>
            </button>
          </div>

          {lastUpdated && (
            <p className="text-sm text-gray-500 mb-4">
              Last analysis: {lastUpdated.toLocaleTimeString()} • Confidence ≥{confidenceThreshold}% • Max {maxRecommendations} stocks
            </p>
          )}

          {/* Recommendations Grid */}
          {showInitialState ? (
            <div className="text-center py-8">
              <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Ready to Analyze</h3>
              <p className="text-gray-600">
                Click "Analyze Watchlist" to generate AI-powered recommendations.
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Current settings: {confidenceThreshold}% confidence • {watchlist.length} stocks in watchlist
              </p>
            </div>
          ) : recommendations.length === 0 ? (
            <div className="text-center py-8">
              <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Strong Signals Found</h3>
              <p className="text-gray-600">
                Try lowering the confidence threshold or check back later for new opportunities.
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Current threshold: {confidenceThreshold}% • Analyzed {watchlist.length} stocks
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {recommendations.map((stock, index) => (
                <div key={`${stock.symbol}-${index}`} className="bg-gray-50 rounded-lg p-6 hover:shadow-md transition-shadow">
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
              ))}
            </div>
          )}
        </div>

        {/* Watchlist Management - SECONDARY FEATURE */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">📋 Watchlist Management</h3>
          
          <div className="flex items-center space-x-2 mb-4">
            <input
              type="text"
              placeholder="Enter symbol (e.g., AAPL)"
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && addToWatchlist()}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => addToWatchlist()}
              className="flex items-center space-x-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add</span>
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {watchlist.map((symbol) => (
              <div key={symbol} className="flex items-center space-x-1 bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                <span className="font-medium">{symbol}</span>
                <button
                  onClick={() => removeFromWatchlist(symbol)}
                  className="text-blue-600 hover:text-blue-800"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>

          {dbStats && (
            <div className="mt-4 text-sm text-gray-600">
              Database: {dbStats.total_stocks} stocks • {dbStats.total_recommendations} historical recommendations • {dbStats.total_prices} price records
            </div>
          )}
        </div>

        {/* Footer */}
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
      </div>
    </div>
  );
}

export default App;