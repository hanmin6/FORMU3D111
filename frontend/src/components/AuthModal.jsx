import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const AuthModal = ({ isOpen, onClose }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    userType: 'spark_partner'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      let result;
      if (isLogin) {
        result = await login(formData.username, formData.password);
      } else {
        result = await register(formData.username, formData.email, formData.password, formData.userType);
      }

      if (result.success) {
        onClose();
        setFormData({ username: '', email: '', password: '', userType: 'spark_partner' });
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('操作失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isLogin ? '登录' : '注册'}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="username">用户名</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              required
              className="input-box"
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label htmlFor="email">邮箱</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                className="input-box"
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password">密码</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              className="input-box"
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label htmlFor="userType">用户类型</label>
              <select
                id="userType"
                name="userType"
                value={formData.userType}
                onChange={handleInputChange}
                className="input-box"
              >
                <option value="spark_partner">星火合伙人 (每周7次)</option>
                <option value="time_curator">时光主理人 (每周100次)</option>
                <option value="founder">创始人 (无限制)</option>
              </select>
            </div>
          )}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-actions">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary"
            >
              {loading ? '处理中...' : (isLogin ? '登录' : '注册')}
            </button>
          </div>
        </form>

        <div className="auth-switch">
          <button
            type="button"
            onClick={() => setIsLogin(!isLogin)}
            className="btn-link"
          >
            {isLogin ? '没有账户？点击注册' : '已有账户？点击登录'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
