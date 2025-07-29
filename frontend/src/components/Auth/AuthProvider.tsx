import React, { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import type { AuthStatus, User } from '../../services/api';
import { apiService } from '../../services/api';

interface AuthContextType {
  authStatus: AuthStatus | null;
  user: User | null;
  loading: boolean;
  login: () => void;
  logout: () => Promise<void>;
  checkAuthStatus: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const checkAuthStatus = async () => {
    try {
      setLoading(true);
      const status = await apiService.getAuthStatus();
      setAuthStatus(status);
      
      if (status.authenticated) {
        // Fetch user profile if authenticated
        try {
          const userProfile = await apiService.getUserProfile();
          setUser(userProfile);
        } catch (error) {
          console.warn('Could not fetch user profile:', error);
        }
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setAuthStatus({ authenticated: false });
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = () => {
    apiService.login();
  };

  const logout = async () => {
    try {
      await apiService.logout();
      setAuthStatus({ authenticated: false });
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
      // Still clear local state even if server logout fails
      setAuthStatus({ authenticated: false });
      setUser(null);
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const value: AuthContextType = {
    authStatus,
    user,
    loading,
    login,
    logout,
    checkAuthStatus,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 