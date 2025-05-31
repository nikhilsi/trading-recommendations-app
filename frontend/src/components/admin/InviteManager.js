// frontend/src/components/admin/InviteManager.js
import React, { useState, useEffect } from 'react';
import { Ticket, Plus, Copy, CheckCircle } from 'lucide-react';
import axios from 'axios';

const InviteManager = () => {
  const [invites, setInvites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [copiedCode, setCopiedCode] = useState('');

  useEffect(() => {
    fetchInvites();
  }, []);

  const fetchInvites = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/auth/invites');
      setInvites(response.data.invites || []);
    } catch (error) {
      console.error('Error fetching invites:', error);
    }
    setLoading(false);
  };

  const createInvite = async () => {
    setCreating(true);
    try {
      const response = await axios.post('/auth/invites', {
        expires_in_days: 7,
        notes: `Created from UI on ${new Date().toLocaleDateString()}`
      });
      
      // Refresh the list
      fetchInvites();
    } catch (error) {
      console.error('Error creating invite:', error);
    }
    setCreating(false);
  };

  const copyToClipboard = (code) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(''), 2000);
  };

  const activeInvites = invites.filter(i => !i.is_used && !i.is_expired);

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <p className="text-sm text-gray-600">
          Manage invite codes for new users
        </p>
        <button
          onClick={createInvite}
          disabled={creating}
          className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          <span>{creating ? 'Creating...' : 'Create Invite'}</span>
        </button>
      </div>

      {loading ? (
        <p className="text-gray-500">Loading invites...</p>
      ) : (
        <div className="space-y-3">
          <p className="text-sm text-gray-600">
            Active invites: {activeInvites.length} • Total: {invites.length}
          </p>
          
          {activeInvites.map((invite) => (
            <div key={invite.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <Ticket className="w-5 h-5 text-purple-600" />
                <code className="font-mono text-sm bg-white px-2 py-1 rounded">
                  {invite.code}
                </code>
                <span className="text-xs text-gray-500">
                  Expires: {new Date(invite.expires_at).toLocaleDateString()}
                </span>
              </div>
              <button
                onClick={() => copyToClipboard(invite.code)}
                className="text-gray-600 hover:text-gray-800"
              >
                {copiedCode === invite.code ? (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </button>
            </div>
          ))}
          
          {activeInvites.length === 0 && (
            <p className="text-gray-500 text-center py-4">
              No active invites. Create one to invite new users.
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default InviteManager;