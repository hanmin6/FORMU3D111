import { useState } from 'react'
import './Settings.css'

function Settings() {
  const [password, setPassword] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [settings, setSettings] = useState({
    cozeAuthorization: '',
    cozeBaseUrl: '',
    pictureAnalysisBotId: '',
    cuteStyleBotId: '',
    steampunkStyleBotId: '',
    japaneseComicStyleBotId: '',
    americanComicStyleBotId: '',
    professionStyleBotId: '',
    cyberpunkStyleBotId: '',
    gothicStyleBotId: '',
    realisticStyleBotId: '',
    soraApiKey: '',
    soraBaseUrl: '',
    tripoApiKey: ''
  })
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleLogin = (e) => {
    e.preventDefault()
    if (password === 'Lihan13230118') {
      setIsAuthenticated(true)
      setMessage('')
      // 加载当前设置
      loadCurrentSettings()
    } else {
      setMessage('密码错误')
    }
  }

  const loadCurrentSettings = async () => {
    try {
      setIsLoading(true)
      const response = await fetch(`${import.meta.env.VITE_API_BASE || 'https://formu-api-production.up.railway.app'}/api/settings`)
      if (response.ok) {
        const data = await response.json()
        setSettings(data)
      }
    } catch (error) {
      console.error('加载设置失败:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSave = async (e) => {
    e.preventDefault()
    try {
      setIsLoading(true)
      const response = await fetch(`${import.meta.env.VITE_API_BASE || 'https://formu-api-production.up.railway.app'}/api/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
      })
      
      if (response.ok) {
        setMessage('设置保存成功！')
      } else {
        setMessage('设置保存失败')
      }
    } catch (error) {
      setMessage('设置保存失败: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }))
  }

  if (!isAuthenticated) {
    return (
      <div className="settings-container">
        <div className="settings-card">
          <h2>管理员登录</h2>
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>密码:</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="请输入管理员密码"
                required
              />
            </div>
            <button type="submit" className="btn-primary">登录</button>
            {message && <div className="message error">{message}</div>}
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="settings-container">
      <div className="settings-card">
        <h2>系统设置</h2>
        <form onSubmit={handleSave}>
          <div className="settings-section">
            <h3>Coze 配置</h3>
            <div className="form-group">
              <label>Coze Authorization:</label>
              <input
                type="password"
                value={settings.cozeAuthorization}
                onChange={(e) => handleInputChange('cozeAuthorization', e.target.value)}
                placeholder="输入 Coze 授权令牌"
              />
            </div>
            <div className="form-group">
              <label>Coze Base URL:</label>
              <input
                type="url"
                value={settings.cozeBaseUrl}
                onChange={(e) => handleInputChange('cozeBaseUrl', e.target.value)}
                placeholder="输入 Coze 基础URL"
              />
            </div>
          </div>

          <div className="settings-section">
            <h3>Bot ID 配置</h3>
            <div className="form-group">
              <label>图片分析 Bot ID:</label>
              <input
                type="text"
                value={settings.pictureAnalysisBotId}
                onChange={(e) => handleInputChange('pictureAnalysisBotId', e.target.value)}
                placeholder="输入图片分析 Bot ID"
              />
            </div>
            <div className="form-group">
              <label>可爱风格 Bot ID:</label>
              <input
                type="text"
                value={settings.cuteStyleBotId}
                onChange={(e) => handleInputChange('cuteStyleBotId', e.target.value)}
                placeholder="输入可爱风格 Bot ID"
              />
            </div>
            <div className="form-group">
              <label>蒸汽朋克风格 Bot ID:</label>
              <input
                type="text"
                value={settings.steampunkStyleBotId}
                onChange={(e) => handleInputChange('steampunkStyleBotId', e.target.value)}
                placeholder="输入蒸汽朋克风格 Bot ID"
              />
            </div>
            <div className="form-group">
              <label>日漫风格 Bot ID:</label>
              <input
                type="text"
                value={settings.japaneseComicStyleBotId}
                onChange={(e) => handleInputChange('japaneseComicStyleBotId', e.target.value)}
                placeholder="输入日漫风格 Bot ID"
              />
            </div>
            <div className="form-group">
              <label>美漫风格 Bot ID:</label>
              <input
                type="text"
                value={settings.americanComicStyleBotId}
                onChange={(e) => handleInputChange('americanComicStyleBotId', e.target.value)}
                placeholder="输入美漫风格 Bot ID"
              />
            </div>
            <div className="form-group">
              <label>职业风格 Bot ID:</label>
              <input
                type="text"
                value={settings.professionStyleBotId}
                onChange={(e) => handleInputChange('professionStyleBotId', e.target.value)}
                placeholder="输入职业风格 Bot ID"
              />
            </div>
            <div className="form-group">
              <label>赛博朋克风格 Bot ID:</label>
              <input
                type="text"
                value={settings.cyberpunkStyleBotId}
                onChange={(e) => handleInputChange('cyberpunkStyleBotId', e.target.value)}
                placeholder="输入赛博朋克风格 Bot ID"
              />
            </div>
            <div className="form-group">
              <label>哥特风格 Bot ID:</label>
              <input
                type="text"
                value={settings.gothicStyleBotId}
                onChange={(e) => handleInputChange('gothicStyleBotId', e.target.value)}
                placeholder="输入哥特风格 Bot ID"
              />
            </div>
            <div className="form-group">
              <label>写实风格 Bot ID:</label>
              <input
                type="text"
                value={settings.realisticStyleBotId}
                onChange={(e) => handleInputChange('realisticStyleBotId', e.target.value)}
                placeholder="输入写实风格 Bot ID"
              />
            </div>
          </div>

          <div className="settings-section">
            <h3>Sora 配置</h3>
            <div className="form-group">
              <label>Sora API Key:</label>
              <input
                type="password"
                value={settings.soraApiKey}
                onChange={(e) => handleInputChange('soraApiKey', e.target.value)}
                placeholder="输入 Sora API 密钥"
              />
            </div>
            <div className="form-group">
              <label>Sora Base URL:</label>
              <input
                type="url"
                value={settings.soraBaseUrl}
                onChange={(e) => handleInputChange('soraBaseUrl', e.target.value)}
                placeholder="输入 Sora 基础URL"
              />
            </div>
          </div>

          <div className="settings-section">
            <h3>Tripo 配置</h3>
            <div className="form-group">
              <label>Tripo API Key:</label>
              <input
                type="password"
                value={settings.tripoApiKey}
                onChange={(e) => handleInputChange('tripoApiKey', e.target.value)}
                placeholder="输入 Tripo API 密钥"
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={isLoading}>
              {isLoading ? '保存中...' : '保存设置'}
            </button>
            <button type="button" className="btn-secondary" onClick={() => setIsAuthenticated(false)}>
              退出
            </button>
          </div>
          
          {message && <div className={`message ${message.includes('成功') ? 'success' : 'error'}`}>{message}</div>}
        </form>
      </div>
    </div>
  )
}

export default Settings
