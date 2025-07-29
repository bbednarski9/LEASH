import React from 'react';
import { useAuth } from './AuthProvider';

const LoginScreen: React.FC = () => {
  const { login, loading } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Pet Calendar Manager</h1>
          <p className="text-gray-600">Manage your pet's schedule with Google Calendar integration</p>
        </div>

        <div className="space-y-4">
          <button
            onClick={login}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <span>Sign in with Google</span>
            )}
          </button>

          <div className="text-center text-sm text-gray-500">
            <p>You'll be redirected to Google to sign in</p>
            <p className="mt-1">We'll only access your calendar data</p>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="text-center text-xs text-gray-400">
            <p>Secure authentication powered by Google OAuth</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen; 