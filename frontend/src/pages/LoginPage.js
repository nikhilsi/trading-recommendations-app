// frontend/src/pages/LoginPage.js
import React, { useState } from 'react';
import LoginForm from '../components/auth/LoginForm';
import RegisterForm from '../components/auth/RegisterForm';

const LoginPage = () => {
  const [showRegister, setShowRegister] = useState(false);
  
  const handleAuthSuccess = () => {
    // Redirect to main app
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Trading Intelligence Platform
        </h1>
        <p className="text-gray-600">
          Professional Stock Market Scanner & AI Recommendations
        </p>
      </div>
      
      {showRegister ? (
        <RegisterForm 
          onSuccess={handleAuthSuccess}
          onLoginClick={() => setShowRegister(false)}
        />
      ) : (
        <LoginForm 
          onSuccess={handleAuthSuccess}
          onRegisterClick={() => setShowRegister(true)}
        />
      )}
      
      <div className="mt-8 text-center text-sm text-gray-500">
        <p>Invite-only platform • Professional trading tools</p>
      </div>
    </div>
  );
};

export default LoginPage;