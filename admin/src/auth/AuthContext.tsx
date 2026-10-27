import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/adminApi';
import type { AdminUser, AdminRole } from '../types/admin';

interface AuthContextType {
  admin: AdminUser | null;
  token: string | null;
  role: AdminRole | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  loading: boolean;
  loginWithKey: (adminKey: string) => Promise<void>;
  loginWithCredentials: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (roles: AdminRole | AdminRole[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [admin, setAdmin] = useState<AdminUser | null>(() => {
    try {
      const saved = localStorage.getItem('saarthi_admin_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem('saarthi_admin_token')
  );

  const [isInitialLoading, setIsInitialLoading] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    const verifySession = async () => {
      const storedToken = localStorage.getItem('saarthi_admin_token');
      if (!storedToken) {
        setIsInitialLoading(false);
        return;
      }

      try {
        const res = await authApi.verify();
        if (res.authenticated && res.admin) {
          setAdmin(res.admin);
          localStorage.setItem('saarthi_admin_user', JSON.stringify(res.admin));
        } else {
          handleLogout();
        }
      } catch {
        handleLogout();
      } finally {
        setIsInitialLoading(false);
      }
    };

    const handleUnauthorized = () => {
      handleLogout();
    };

    window.addEventListener('saarthi-admin-unauthorized', handleUnauthorized);
    verifySession();

    return () => {
      window.removeEventListener('saarthi-admin-unauthorized', handleUnauthorized);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('saarthi_admin_token');
    localStorage.removeItem('saarthi_admin_user');
    setToken(null);
    setAdmin(null);
  };

  const loginWithKey = async (adminKey: string) => {
    setIsLoading(true);
    try {
      const res = await authApi.login({ admin_key: adminKey });
      localStorage.setItem('saarthi_admin_token', res.token);
      localStorage.setItem('saarthi_admin_user', JSON.stringify(res.admin));
      setToken(res.token);
      setAdmin(res.admin);
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithCredentials = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await authApi.login({ email, password });
      localStorage.setItem('saarthi_admin_token', res.token);
      localStorage.setItem('saarthi_admin_user', JSON.stringify(res.admin));
      setToken(res.token);
      setAdmin(res.admin);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authApi.logout().catch(() => null);
    } finally {
      handleLogout();
    }
  };

  const hasRole = (roles: AdminRole | AdminRole[]): boolean => {
    if (!admin?.role) return false;
    if (admin.role === 'SUPER_ADMIN') return true;
    const requiredRoles = Array.isArray(roles) ? roles : [roles];
    return requiredRoles.includes(admin.role);
  };

  return (
    <AuthContext.Provider
      value={{
        admin,
        token,
        role: admin?.role || null,
        isAuthenticated: !!token && !!admin,
        isLoading,
        loading: isInitialLoading,
        loginWithKey,
        loginWithCredentials,
        logout,
        hasRole
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAdminAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAdminAuth must be used within an AuthProvider');
  }
  return context;
};

export const useAuth = useAdminAuth;
