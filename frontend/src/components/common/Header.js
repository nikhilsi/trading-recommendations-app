// frontend/src/components/common/Header.js
import React from 'react';
import { Settings, LogOut, User, Shield } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const Header = ({ showSettings, onToggleSettings, showAdmin, onToggleAdmin }) => {
  const { user, isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      logout();
      window.location.reload();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Stock Trading Intelligence</h1>
          <p className="text-gray-600 mt-1">
            Market Scanner & AI-Powered Recommendations
          </p>
        </div>
        <div className="flex items-center space-x-3">
          {isAuthenticated && (
            <>
              <div className="flex items-center space-x-2 text-sm text-gray-600 px-3 py-1 bg-gray-100 rounded-lg">
                <User className="w-4 h-4" />
                <span>{user?.email}</span>
                {user?.is_admin && (
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">
                    Admin
                  </span>
                )}
              </div>
              
              {user?.is_admin && (
                <button 
                  onClick={onToggleAdmin}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    showAdmin 
                      ? 'bg-purple-600 text-white' 
                      : 'bg-purple-100 hover:bg-purple-200 text-purple-700'
                  }`}
                >
                  <Shield className="w-4 h-4" />
                  <span>Admin</span>
                </button>
              )}
              
              <button 
                onClick={onToggleSettings}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  showSettings 
                    ? 'bg-gray-600 text-white' 
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                }`}
              >
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </button>
              
              <button 
                onClick={handleLogout}
                className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Header;