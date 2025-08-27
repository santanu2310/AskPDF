import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService, AuthUser } from '@/lib/auth';

interface AuthContextType {
  user: AuthUser | null;
  isGuest: boolean;
  isLoading: boolean;
  login: (provider: "google" | "github") => Promise<void>;
  logout: () => Promise<void>;
  requireAuth: () => Promise<boolean>;
  checkAuth: (userData?: AuthUser | null) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isGuest, setIsGuest] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const checkAuth = async (userData?: AuthUser | null) => {
    if (!userData) userData = await authService.getCurrentUser();
    if (userData) {
      setUser(userData);
      setIsGuest(false);
      return true;
    }
    return false;
  };

  const login = async (provider: "google" | "github") => {
    setIsLoading(true);
    await authService.initiateOAuth(provider);
    setIsLoading(false);
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    setIsGuest(true);
  };

  const requireAuth = async () => {
    if (user) return true;
    return await checkAuth();
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ user, isGuest, isLoading, login, logout, requireAuth, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
