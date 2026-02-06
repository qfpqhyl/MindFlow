# MindFlow Frontend

极简主义风格的 React 前端应用。

## 设计理念

**瑞士国际主义风格 + 现代极简主义**

- **调色板**: 纯黑 (#000) + 纯白 (#FFF) + 精确的灰阶系统
- **字体**: Inter (正文) + JetBrains Mono (代码)
- **设计原则**: 极致克制、网格系统、精确对齐、大量留白
- **视觉特征**: 锐利的边框、1px 分隔线、微妙的阴影、高对比度

## 技术栈

- **框架**: React 18 + Vite
- **UI 库**: MUI (Material-UI) v6
- **路由**: React Router v6
- **HTTP 客户端**: Axios
- **状态管理**: React Context
- **日期处理**: MUI X Date Pickers

## 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 构建生产版本

```bash
npm run build
```

## 项目结构

```
src/
├── components/          # 共享组件
│   └── Layout.jsx       # 主布局（导航栏 + 侧边栏）
├── contexts/            # React Context
│   └── AuthContext.jsx  # 认证上下文
├── pages/               # 页面组件
│   ├── LoginPage.jsx           # 登录/注册页
│   ├── ConversationsPage.jsx   # 对话列表
│   ├── ChatPage.jsx            # 聊天界面
│   ├── DocumentsPage.jsx       # 文档列表
│   ├── TasksPage.jsx           # 任务列表
│   └── SettingsPage.jsx        # 设置页面
├── services/            # API 服务
│   └── api.js           # API 客户端封装
├── theme.js             # MUI 主题配置
├── App.jsx              # 主应用组件
└── main.jsx             # 应用入口
```

## 核心功能

### 1. 认证模块
- 用户登录/注册
- JWT token 管理
- 自动登录
- 路由保护

### 2. 对话管理
- 对话列表（卡片式布局）
- 创建新对话
- 删除对话
- 搜索对话

### 3. AI 聊天
- 实时聊天界面
- 消息历史显示
- 用户/AI 消息区分
- 快捷键支持（Enter 发送，Shift+Enter 换行）
- 整理为文档功能

### 4. 文档管理
- 文档列表（卡片式布局）
- 创建文档
- 编辑/删除文档
- 标签系统
- 搜索文档

### 5. 任务管理
- 任务列表
- 状态筛选（全部/进行中/已完成/已逾期）
- 创建任务
- 完成任务
- 日期选择器

### 6. 用户设置
- 个人信息编辑
- 邮件设置
- 密码修改
- AI 模型选择

## 设计特点

### 极简主义美学
1. **纯黑白配色**
   - 主色: #000000
   - 背景: #FFFFFF
   - 分隔线: #E0E0E0
   - 文字: #000000

2. **锐利的边角**
   - 所有组件 borderRadius: 0
   - 1px 边框
   - 精确的网格对齐

3. **精确的间距系统**
   - 统一的 padding/margin
   - 基于网格的布局
   - 大量留白

4. **微妙的交互**
   - 悬停效果
   - 状态反馈
   - 平滑过渡

### 响应式设计
- 移动端优先
- 自适应布局
- 抽屉式导航（移动端）
- 固定侧边栏（桌面端）

## API 集成

所有 API 请求通过 `services/api.js` 统一管理：

```javascript
import { conversationsAPI, messagesAPI } from './services/api';

// 获取对话列表
const response = await conversationsAPI.getList();

// 发送消息
await messagesAPI.send(conversationId, { content, stream: false });
```

## 状态管理

使用 React Context 进行全局状态管理：

```javascript
import { useAuth } from './contexts/AuthContext';

const { user, login, logout } = useAuth();
```

## 开发规范

### 组件规范
- 使用函数式组件
- Hooks 状态管理
- Props 验证（PropTypes）
- 清晰的命名

### 代码风格
- ESLint + Prettier
- 2 空格缩进
- 单引号
- 无分号（可选）

### Git 提交规范
```
feat: 添加新功能
fix: 修复 bug
style: 代码格式调整
refactor: 重构
docs: 文档更新
```

## 环境变量

创建 `.env.local` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 部署

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

### 静态托管

构建后的文件在 `dist/` 目录，可以部署到：
- Netlify
- Vercel
- GitHub Pages
- 任何静态文件服务器

## 已知问题

1. **AI 功能**: 需要配置真实的 NVIDIA API KEY
2. **邮件功能**: 需要配置 SMTP 服务
3. **WebSocket**: 待实现实时通信

## 后续计划

### Phase 1: 基础功能 ✅
- [x] 用户认证
- [x] 对话管理
- [x] AI 聊天
- [x] 文档管理
- [x] 任务管理

### Phase 2: 增强功能
- [ ] WebSocket 实时通信
- [ ] 富文本编辑器
- [ ] 文件上传
- [ ] 导出功能

### Phase 3: 优化
- [ ] 性能优化
- [ ] 离线支持
- [ ] PWA
- [ ] 国际化

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License

---

**设计**: 瑞士国际主义风格
**实现**: React + MUI
**配色**: 纯黑 + 纯白
