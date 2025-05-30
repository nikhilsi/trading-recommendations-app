// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';

// Components
import Header from './components/common/Header';
import ErrorMessage from './components/common/ErrorMessage';
import StatsCards from './components/common/StatsCards';
import MarketScanner from './components/market-scanner/MarketScanner';
import RecommendationsList from './components/recommendations/RecommendationsList';
import WatchlistManager from './components/watchlist/WatchlistManager';
import SettingsPanel from './components/common/SettingsPanel';
import Footer from './components/common/Footer';

// Hooks
import { useMarketScanner } from './hooks/useMarketScanner';
import { useRecommendations } from './hooks/useRecommendations';
import { useWatchlist } from './hooks/useWatchlist';
import { useStats } from './hooks/useStats';

function App() {
  const [showSettings, setShowSettings] = useState(false);
  const [error] = useState(null);
  
  // Use custom hooks
  const marketScanner = useMarketScanner();
  const recommendations = useRecommendations();
  const watchlist = useWatchlist();
  const stats = useStats();

  // Initial data load
  useEffect(() => {
    watchlist.fetch();
    stats.fetch();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Refresh stats when recommendations update
  useEffect(() => {
    stats.fetch();
  }, [recommendations.confidenceThreshold, recommendations.maxRecommendations, stats.fetch]); 

  // Combine errors from different sources
  const currentError = error || marketScanner.error || recommendations.error || watchlist.error;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        <Header 
          showSettings={showSettings}
          onToggleSettings={() => setShowSettings(!showSettings)}
        />

        {showSettings && (
          <SettingsPanel
            confidenceThreshold={recommendations.confidenceThreshold}
            onConfidenceChange={recommendations.setConfidenceThreshold}
            maxRecommendations={recommendations.maxRecommendations}
            onMaxRecommendationsChange={recommendations.setMaxRecommendations}
          />
        )}

        {currentError && <ErrorMessage error={currentError} />}

        <MarketScanner
          opportunities={marketScanner.opportunities}
          scanType={marketScanner.scanType}
          setScanType={marketScanner.setScanType}
          loading={marketScanner.loading}
          lastScanTime={marketScanner.lastScanTime}
          marketStats={marketScanner.marketStats}
          onScan={marketScanner.scan}
          onAddToWatchlist={watchlist.add}
          watchlist={watchlist.symbols}
        />

        <StatsCards
          marketOpportunities={marketScanner.opportunities.length}
          recommendations={recommendations.data.length}
          buySignals={recommendations.data.filter(r => r.action === 'BUY').length}
          sellSignals={recommendations.data.filter(r => r.action === 'SELL').length}
          watchlistSize={watchlist.symbols.length}
        />

        <RecommendationsList
          recommendations={recommendations.data}
          loading={recommendations.loading}
          onRefresh={recommendations.fetch}
          lastUpdated={recommendations.lastUpdated}
          confidenceThreshold={recommendations.confidenceThreshold}
          maxRecommendations={recommendations.maxRecommendations}
          watchlistSize={watchlist.symbols.length}
        />

        <WatchlistManager
          watchlist={watchlist.symbols}
          onAdd={watchlist.add}
          onRemove={watchlist.remove}
          dbStats={stats.data}
        />

        <Footer />
      </div>
    </div>
  );
}

export default App;