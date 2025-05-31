// frontend/src/pages/LoginPage.js
import React from 'react';
import LoginForm from '../components/auth/LoginForm';

const LoginPage = () => {
  const handleLoginSuccess = () => {
    // Redirect to main app or close modal
    window.location.reload(); // Simple reload for now
  };

  const handleRegisterClick = () => {
    // TODO: Show register form
    alert('Registration coming soon! Use your invite code.');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <LoginForm 
        onSuccess={handleLoginSuccess}
        onRegisterClick={handleRegisterClick}
      />
    </div>
  );
};

export default LoginPage;