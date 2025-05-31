// frontend/src/components/admin/AdminPanel.js
import React, { useState } from 'react';
import { Shield, Ticket, Users, Activity } from 'lucide-react';
import InviteManager from './InviteManager';

const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('invites');

  const tabs = [
    { id: 'invites', label: 'Invites', icon: Ticket },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'stats', label: 'Platform Stats', icon: Activity },
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
      <div className="flex items-center space-x-2 mb-4">
        <Shield className="w-5 h-5 text-purple-600" />
        <h3 className="text-lg font-semibold">Admin Panel</h3>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 border-b">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'text-purple-600 border-b-2 border-purple-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'invites' && <InviteManager />}
        
        {activeTab === 'users' && (
          <div className="text-center py-8 text-gray-500">
            <Users className="w-12 h-12 mx-auto mb-2 text-gray-400" />
            <p>User management coming soon</p>
            <p className="text-sm">View all users, activity, and permissions</p>
          </div>
        )}
        
        {activeTab === 'stats' && (
          <div className="text-center py-8 text-gray-500">
            <Activity className="w-12 h-12 mx-auto mb-2 text-gray-400" />
            <p>Platform statistics coming soon</p>
            <p className="text-sm">Usage metrics, growth, and analytics</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPanel;