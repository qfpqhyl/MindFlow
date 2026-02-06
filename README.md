# MindFlow

<div align="center">

**智能工作流应用 - 集成聊天、文档管理和定时任务**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue)](https://reactjs.org)
[![MUI](https://img.shields.io/badge/MUI-v6-blue)](https://mui.com)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## 📋 项目简介

MindFlow 是一个智能工作流应用，将 AI 聊天、知识管理和任务提醒完美整合。通过对话生成文档、自动创建任务并设置邮件提醒，让您的工作流更加高效。

### ✨ 核心功能

- 🤖 **AI 智能对话** - 基于 NVIDIA Llama 3.1 模型，支持流式输出
- 📝 **智能文档生成** - 一键将对话整理成结构化文档
- 📋 **定时任务管理** - 从文档直接创建任务，支持邮件提醒
- 🔍 **全文搜索** - 快速找到需要的内容
- 🏷️ **标签系统** - 灵活组织文档和知识
- 📧 **邮件提醒** - 飞书 SMTP 集成，任务到期自动提醒
- 🎨 **极简设计** - 黑白配色，专注内容

### 🎯 使用场景

- 会议记录整理
- 学习笔记生成
- 项目任务追踪
- 知识库管理
- 待办事项提醒

## 🏗️ 项目架构

```
MindFlow/
├── backend/                 # 后端服务 (FastAPI)
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 数据库模型
│   │   ├── auth.py         # 认证工具
│   │   ├── ai_service.py   # NVIDIA AI 服务
│   │   ├── email_service.py # 邮件服务
│   │   ├── scheduler.py    # 任务调度器
│   │   └── schemas.py      # 数据模型
│   ├── main.py             # 应用入口
│   ├── requirements.txt    # Python 依赖
│   └── .env.example        # 环境变量模板
├── frontend/               # 前端应用 (React + Vite)
│   ├── src/
│   │   ├── components/     # React 组件
│   │   │   └── Layout.jsx  # 主布局组件
│   │   ├── pages/          # 页面组件
│   │   │   ├── LoginPage.jsx
│   │   │   ├── ConversationsPage.jsx
│   │   │   ├── ChatPage.jsx
│   │   │   ├── DocumentsPage.jsx
│   │   │   ├── TasksPage.jsx
│   │   │   └── SettingsPage.jsx
│   │   ├── services/       # API 服务
│   │   ├── contexts/       # React Context
│   │   └── theme.js        # MUI 主题配置
│   ├── package.json        # Node 依赖
│   └── vite.config.js      # Vite 配置
└── README.md               # 项目文档
```

## 🚀 快速开始

### 环境要求

**后端：**
- Python 3.8+
- pip

**前端：**
- Node.js 16+
- npm 或 yarn

### 后端服务安装

#### 1. 克隆项目

```bash
git clone <repository-url>
cd MindFlow
```

#### 2. 安装依赖

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下关键参数：

```env
# NVIDIA API（必需）
NVIDIA_API_KEY=your_nvidia_api_key_here

# 邮件服务（可选）
SMTP_HOST=smtp.feishu.cn
SMTP_PORT=465
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_password
EMAIL_FROM=your_email@example.com

# JWT 密钥（生产环境请修改）
SECRET_KEY=your-secret-key-here
```

**获取 NVIDIA API Key：**
1. 访问 [https://build.nvidia.com](https://build.nvidia.com)
2. 注册/登录账号
3. 生成 API Key

#### 4. 初始化数据库

数据库会在首次运行时自动创建。

#### 5. 启动服务

```bash
# 方式一：使用启动脚本
./start.sh  # macOS/Linux
start.bat   # Windows

# 方式二：直接运行
python main.py
```

API 服务将在 http://localhost:8000 启动

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 前端应用安装

#### 1. 安装依赖

```bash
cd frontend
npm install
```

#### 2. 启动开发服务器

```bash
npm run dev
```

前端应用将在 http://localhost:5173 启动

#### 3. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

## 📚 功能说明

### 1. 用户认证

- 支持用户注册和登录
- JWT 令牌认证
- 密码 bcrypt 加密存储
- 自动刷新令牌

### 2. AI 对话

- 基于 NVIDIA Llama 3.1 模型
- 支持流式输出（逐字显示）
- 自动保存对话历史
- 支持多轮对话

### 3. 对话管理

- 创建/编辑/删除对话
- 对话列表搜索
- 消息统计

### 4. 文档管理

- 一键将对话整理为文档
- AI 自动生成摘要和标签
- 文档编辑和删除
- 全文搜索

### 5. 任务管理

- 从文档创建任务
- 设置截止日期
- 任务状态跟踪（待办/完成/过期）
- 邮件提醒集成

### 6. 邮件提醒

- 任务到期自动发送邮件
- 支持飞书 SMTP
- 可配置提醒邮箱
- 提醒历史记录

## 📚 API 文档

### 认证模块

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录 |
| POST | `/api/v1/auth/refresh` | 刷新令牌 |

### 对话管理

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/v1/conversations` | 获取对话列表 |
| POST | `/api/v1/conversations` | 创建对话 |
| GET | `/api/v1/conversations/{id}` | 获取对话详情 |
| PUT | `/api/v1/conversations/{id}` | 更新对话标题 |
| DELETE | `/api/v1/conversations/{id}` | 删除对话 |

### 消息管理

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/v1/conversations/{id}/messages` | 获取消息列表 |
| POST | `/api/v1/conversations/{id}/messages` | 发送消息（非流式）|
| POST | `/api/v1/conversations/{id}/messages/stream` | 发送消息（流式 SSE）|

### 整理功能

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/organize/to-document` | 整理对话为文档 |
| POST | `/api/v1/organize/suggestions` | 获取整理建议 |

### 文档管理

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/v1/documents` | 获取文档列表 |
| POST | `/api/v1/documents` | 创建文档 |
| GET | `/api/v1/documents/{id}` | 获取文档详情 |
| PUT | `/api/v1/documents/{id}` | 更新文档 |
| DELETE | `/api/v1/documents/{id}` | 删除文档 |
| GET | `/api/v1/documents/search` | 搜索文档 |

### 任务管理

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/v1/tasks` | 获取任务列表 |
| POST | `/api/v1/tasks` | 创建任务 |
| PUT | `/api/v1/tasks/{id}` | 更新任务 |
| POST | `/api/v1/tasks/{id}/complete` | 完成任务 |
| DELETE | `/api/v1/tasks/{id}` | 删除任务 |
| POST | `/api/v1/tasks/{id}/send-reminder` | 发送提醒邮件 |

详细 API 文档请访问：http://localhost:8000/docs

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI 0.115.0
- **数据库**: SQLite 3
- **AI**: NVIDIA API (Llama 3.1 405B)
- **认证**: JWT + bcrypt
- **邮件**: 飞书 SMTP
- **调度**: APScheduler
- **异步**: httpx + asyncio

### 前端
- **框架**: React 18 + Vite
- **UI 库**: MUI v6 (Material-UI)
- **状态管理**: React Context API
- **路由**: React Router v6
- **HTTP 客户端**: Axios
- **日期处理**: date-fns
- **样式**: 自定义黑白主题

## 🎨 设计特色

- **极简美学**: 纯黑纯白配色，去除多余装饰
- **国际化字体**: Inter + JetBrains Mono
- **响应式布局**: 完美适配桌面和移动端
- **无滚动条**: 隐藏滚动条，保持界面整洁
- **流式体验**: AI 回复逐字显示，实时反馈

## 🔐 安全性

- ✅ 密码使用 bcrypt 加密存储
- ✅ JWT 令牌认证
- ✅ 参数化查询防止 SQL 注入
- ✅ CORS 跨域配置
- ✅ 输入验证和错误处理
- ✅ 敏感信息环境变量管理

## 📝 开发路线图

### Phase 1: 基础功能 ✅
- [x] 用户认证系统
- [x] 对话管理 CRUD
- [x] AI 聊天功能

### Phase 2: 核心功能 ✅
- [x] 整理命令（对话转文档）
- [x] 文档管理完整功能
- [x] 定时任务管理
- [x] 邮件提醒集成

### Phase 3: 前端开发 ✅
- [x] React + Vite 项目搭建
- [x] MUI 组件库集成
- [x] 所有页面开发完成
- [x] 流式输出实现
- [x] 响应式布局优化

### Phase 4: 增强功能 🚧
- [ ] WebSocket 实时通信
- [ ] 文档全文搜索优化
- [ ] 多语言支持
- [ ] 数据导入导出
- [ ] 移动端应用

## 🧪 测试

运行 API 测试脚本：

```bash
cd backend
python test_api.py
```

## 🔧 常见问题

### 1. NVIDIA API 调用失败

**错误**: `Error: API returned status 401`

**解决**: 检查 `.env` 文件中的 `NVIDIA_API_KEY` 是否正确配置。

### 2. 邮件发送失败

**错误**: SMTP 连接超时

**解决**: 检查邮箱配置和 SMTP 服务器设置，确保网络可访问。

### 3. 前端无法连接后端

**错误**: Network Error 或 CORS 错误

**解决**:
- 确认后端服务已启动（http://localhost:8000）
- 检查 `vite.config.js` 中的 proxy 配置

### 4. 数据库错误

**错误**: `sqlite3.OperationalError: no such table`

**解决**: 删除 `backend/data/mindflow.db`，重启后端自动创建新数据库。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 许可证

MIT License

## 📮 联系方式

如有问题或建议，请提交 Issue。

---

<div align="center">

Made with ❤️ by MindFlow Team

**⭐ 如果这个项目对你有帮助，请给个 Star！**

</div>
