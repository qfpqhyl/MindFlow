# MindFlow

<div align="center">

**智能工作流应用 - 集成聊天、文档管理和定时任务**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## 📋 项目简介

MindFlow 是一个智能工作流应用，将 AI 聊天、知识管理和任务提醒完美整合。通过对话生成文档、自动创建任务并设置邮件提醒，让您的工作流更加高效。

### ✨ 核心功能

- 🤖 **AI 智能对话** - 基于 NVIDIA Llama 3.1 模型
- 📝 **智能文档生成** - 一键将对话整理成结构化文档
- 📋 **定时任务管理** - 从文档直接创建任务，支持邮件提醒
- 🔍 **全文搜索** - 快速找到需要的内容
- 🏷️ **标签系统** - 灵活组织文档和知识
- 📧 **邮件提醒** - 飞书 SMTP 集成，任务到期自动提醒

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
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端应用 (React + Vite)
│   ├── src/
│   │   ├── components/     # React 组件
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API 服务
│   │   └── utils/          # 工具函数
│   └── package.json        # Node 依赖
└── README.md               # 项目文档
```

## 🚀 快速开始

### 后端服务

#### 1. 环境要求

- Python 3.8+
- pip

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
# 编辑 .env 文件，配置 NVIDIA API_KEY 和邮件设置
```

#### 4. 启动服务

```bash
./start.sh  # macOS/Linux
# 或
start.bat   # Windows
```

API 服务将在 http://localhost:8000 启动

文档地址：http://localhost:8000/docs

### 前端应用（开发中）

```bash
cd frontend
npm install
npm run dev
```

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
| PUT | `/api/v1/conversations/{id}` | 更新对话 |
| DELETE | `/api/v1/conversations/{id}` | 删除对话 |

### 消息管理

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/v1/conversations/{id}/messages` | 获取消息列表 |
| POST | `/api/v1/conversations/{id}/messages` | 发送消息 |

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

### 任务管理

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/v1/tasks` | 获取任务列表 |
| POST | `/api/v1/tasks` | 创建任务 |
| PUT | `/api/v1/tasks/{id}` | 更新任务 |
| POST | `/api/v1/tasks/{id}/complete` | 完成任务 |
| DELETE | `/api/v1/tasks/{id}` | 删除任务 |

更多详细信息请查看 [API 设计文档](./backend/README.md)

## 🧪 测试

运行 API 测试脚本：

```bash
cd backend
python test_api.py
```

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI 0.115.0
- **数据库**: SQLite 3
- **AI**: NVIDIA API (Llama 3.1)
- **认证**: JWT
- **邮件**: 飞书 SMTP
- **调度**: APScheduler

### 前端
- **框架**: React + Vite
- **UI**: TailwindCSS
- **状态管理**: React Context
- **HTTP 客户端**: Axios

## 🔐 安全性

- 密码使用 bcrypt 加密
- JWT 令牌认证
- 参数化查询防止 SQL 注入
- CORS 配置
- 输入验证

## 📝 开发路线图

### Phase 1: 基础功能 ✅
- [x] 用户认证
- [x] 对话管理
- [x] AI 聊天功能

### Phase 2: 核心功能 ✅
- [x] 整理命令（对话转文档）
- [x] 文档管理
- [x] 定时任务管理
- [x] 邮件提醒

### Phase 3: 增强功能
- [ ] WebSocket 实时通信
- [ ] 前端界面开发
- [ ] 文档全文搜索优化
- [ ] 多语言支持
- [ ] 数据导入导出

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📮 联系方式

如有问题或建议，请提交 Issue。

---

<div align="center">

Made with ❤️ by MindFlow Team

</div>
