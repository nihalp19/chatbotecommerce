import React, { useEffect } from 'react';
import { AuthPage } from './components/auth/AuthPage';
import { ChatWindow } from './components/chat/ChatWindow';
import { useAuthStore } from './stores/authStore';

function App() {
  const { user, loading, checkAuthStatus } = useAuthStore();

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return user ? <ChatWindow /> : <AuthPage />;
}

export default App;
