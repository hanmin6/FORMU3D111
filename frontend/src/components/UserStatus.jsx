import { useAuth } from '../contexts/AuthContext';

const UserStatus = () => {
  const { user, userStatus, logout, canUse3D, canSeePrompts, remainingUsage, weeklyLimit, usageThisWeek } = useAuth();

  if (!user) return null;

  const getUserTypeDisplay = (userType) => {
    switch (userType) {
      case 'spark_partner':
        return '星火合伙人';
      case 'time_curator':
        return '时光主理人';
      case 'founder':
        return '创始人';
      default:
        return userType;
    }
  };

  const getUsageDisplay = () => {
    if (weeklyLimit === -1) {
      return '无限制';
    }
    return `${usageThisWeek}/${weeklyLimit}`;
  };

  const getRemainingDisplay = () => {
    if (weeklyLimit === -1) {
      return '无限制';
    }
    return remainingUsage;
  };

  return (
    <div className="user-status">
      <div className="user-info">
        <div className="user-badge">
          <span className="user-type">{getUserTypeDisplay(user.user_type)}</span>
          <span className="user-name">{user.username}</span>
        </div>
        <button className="logout-btn" onClick={logout} title="退出登录">
          🚪
        </button>
      </div>
      
      <div className="usage-info">
        <div className="usage-item">
          <span className="usage-label">本周使用:</span>
          <span className="usage-value">{getUsageDisplay()}</span>
        </div>
        <div className="usage-item">
          <span className="usage-label">剩余次数:</span>
          <span className="usage-value">{getRemainingDisplay()}</span>
        </div>
      </div>

      <div className="permissions">
        <div className="permission-item">
          <span className="permission-label">3D功能:</span>
          <span className={`permission-value ${canUse3D ? 'allowed' : 'denied'}`}>
            {canUse3D ? '✅ 可用' : '❌ 不可用'}
          </span>
        </div>
        <div className="permission-item">
          <span className="permission-label">查看提示词:</span>
          <span className={`permission-value ${canSeePrompts ? 'allowed' : 'denied'}`}>
            {canSeePrompts ? '✅ 可见' : '❌ 隐藏'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default UserStatus;
