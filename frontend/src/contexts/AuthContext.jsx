import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('auth_token'));
  const [userStatus, setUserStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  // 检查token是否有效并获取用户信息
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const response = await fetch('/api/auth/me', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
            
            // 获取用户状态信息
            const statusResponse = await fetch('/api/auth/status', {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            });
            
            if (statusResponse.ok) {
              const statusData = await statusResponse.json();
              setUserStatus(statusData);
            }
          } else {
            // Token无效，清除本地存储
            localStorage.removeItem('auth_token');
            setToken(null);
          }
        } catch (error) {
          console.error('Auth check failed:', error);
          localStorage.removeItem('auth_token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        setUser(data.user);
        localStorage.setItem('auth_token', data.access_token);
        
        // 获取用户状态信息
        const statusResponse = await fetch('/api/auth/status', {
          headers: {
            'Authorization': `Bearer ${data.access_token}`
          }
        });
        
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          setUserStatus(statusData);
        }
        
        return { success: true };
      } else {
        const error = await response.json();
        return { success: false, error: error.detail || '登录失败' };
      }
    } catch (error) {
      return { success: false, error: '网络错误' };
    }
  };

  const register = async (username, email, password, userType) => {
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password, user_type: userType }),
      });

      if (response.ok) {
        return { success: true };
      } else {
        const error = await response.json();
        return { success: false, error: error.detail || '注册失败' };
      }
    } catch (error) {
      return { success: false, error: '网络错误' };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setUserStatus(null);
    localStorage.removeItem('auth_token');
  };

  const refreshUserStatus = async () => {
    if (token) {
      try {
        const response = await fetch('/api/auth/status', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const statusData = await response.json();
          setUserStatus(statusData);
        }
      } catch (error) {
        console.error('Failed to refresh user status:', error);
      }
    }
  };

  const value = {
    user,
    token,
    userStatus,
    loading,
    login,
    register,
    logout,
    refreshUserStatus,
    isAuthenticated: !!user,
    canUse3D: userStatus?.can_use_3d || false,
    canSeePrompts: userStatus?.can_see_prompts || false,
    remainingUsage: userStatus?.remaining_usage || 0,
    weeklyLimit: userStatus?.weekly_limit || 0,
    usageThisWeek: userStatus?.usage_this_week || 0,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
