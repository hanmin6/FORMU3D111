# FORMU



![FORMU 展示](frontend/static/show.png) 



**FORMU** 是一款现代化的 Web 应用，它能将你的二维图片转换为令人惊叹的三维模型。通过强大的 AI 服务，它提供了从图片分析、创意提示词生成到最终 3D 模型创建的无缝工作流，并配备了一个美观、实时交互的界面。

---

### ✨ 核心功能

*   **AI 驱动的 3D 模型生成**：通过 Tripo3D API 将静态图片转换为完整渲染的 `.glb` 3D 模型。
*   **智能图片分析**：集成 Coze API 深度理解用户上传图片的内容与上下文。
*   **多风格提示词生成**：基于图片分析生成高质量的创意提示词，支持多种风格（如：写实、可爱、赛博朋克）。
*   **实时用户体验**：使用 WebSockets 和 SSE（服务器发送事件）提供实时进度更新，并带有“打字机效果”。
*   **现代化交互式 UI**：
    *   精美的 3D 轮播展示，带来沉浸式视觉体验。
    *   玻璃拟态风格设计，支持折叠侧边栏。
    *   支持拖拽上传图片和粘贴图片 URL。
    *   弹窗编辑器，允许用户调整 AI 生成的文本。
*   **完整的用户与项目管理**：
    *   基于 JWT 的安全用户认证（注册/登录）。
    *   持久化的项目历史，用户可保存、查看、编辑、删除作品。

---

### 🛠️ 技术栈

**后端（Backend）：**
*   **框架**: FastAPI
*   **数据库**: MySQL
*   **认证**: JWT
*   **AI 服务**: Tripo3D API、Coze API
*   **实时通信**: WebSockets
*   **异步 HTTP**: httpx
*   **服务器**: Uvicorn

**前端（Frontend）：**
*   **框架**: React 19 (Hooks)
*   **构建工具**: Vite
*   **路由**: React Router
*   **样式**: 现代 CSS（变量、动画）
*   **实时通信**: 原生 `fetch` + SSE 流式传输

---

### 🚀 快速开始

按照以下步骤在本地搭建并运行项目。

#### 前置条件

*   Python 3.12.11 
*   Node.js v22.18.0 与 npm
*   已运行的 MySQL 数据库服务

#### 后端配置

1.  **进入后端目录：**
    ```bash
    cd backend/
    ```

2.  **创建并激活虚拟环境：**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows 使用 `venv\Scripts\activate`
    ```

3.  **安装依赖：**
    ```bash
    pip install -r requirements.txt
    ```

4.  **配置环境变量：**
    在 `backend/` 目录下复制 `.env.example` 文件为 `.env`，并填写相关凭据：
    ```env
    # COZE API
    COZE_BASE_URL=https://api.coze.cn
    COZE_AUTHORIZATION=your_coze_token
    
    PICTURE_ANALYSIS_BOT_ID=...
    # ... 其他 Bot ID
    
    # TRIPO API
    TRIPO_API_KEY="your_tripo_api_key"
    
    # 数据库 (MySQL) - 使用 Railway 标准环境变量名
    MYSQLHOST=localhost
    MYSQLPORT=3306
    MYSQLUSER=root
    MYSQLPASSWORD=your_db_password
    MYSQLDATABASE=FORMU
    
    # Sora API
    SORA_API_KEY=your_sora_api_key
    SORA_BASE_URL=your_sora_base_url
    
    # JWT
    SECRET_KEY=a_very_secret_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

5.  **设置数据库密码环境变量：**
    **重要**：在启动服务器之前，需要设置 MySQL 密码环境变量：
    ```bash
    export MYSQLPASSWORD=your_mysql_password
    ```
    请将 `your_mysql_password` 替换为您的实际 MySQL root 密码。

6.  **初始化数据库：**
    应用启动时会自动创建数据库和表。也可以运行初始化脚本创建管理员账户：
    ```bash
    python scripts/init_db.py --seed
    ```

#### 前端配置

1.  **进入前端目录：**
    ```bash
    cd frontend/
    ```

2.  **安装依赖：**
    ```bash
    npm install
    ```

---

### ▶️ 运行应用

1.  **设置数据库密码环境变量：**
    **重要**：在启动服务器之前，必须先设置 MySQL 密码环境变量：
    ```bash
    export MYSQLPASSWORD=your_mysql_password
    ```
    请将 `your_mysql_password` 替换为您的实际 MySQL root 密码。

2.  **启动后端服务：**
    在 `backend/` 目录下执行：
    ```bash
    python app/run.py
    ```
    后端服务运行在 `http://localhost:8000`

3.  **启动前端开发服务器：**
    在 `frontend/` 目录下执行：
    ```bash
    npm run dev
    ```
    前端服务运行在 `http://localhost:5173`。Vite 已预配置代理转发 API 请求到后端。

---

### 🌟 致谢

*   本项目由 [Tripo3D](https://www.tripo3d.ai/) 与 [Coze](https://www.coze.cn/) 的优秀 API 提供支持。
*   [@困 @一片小叶子🍃 @lavender] 
