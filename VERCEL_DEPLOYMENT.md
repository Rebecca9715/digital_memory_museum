# 🚀 Vercel 部署指南

本指南将帮助您将 DAA_MVP 项目部署到 Vercel，使其可以在线访问。

---

## 📋 前置准备

### 1. 注册 Vercel 账号
访问 https://vercel.com 并注册账号（建议使用 GitHub 账号登录）

### 2. 安装 Vercel CLI（可选）
```bash
npm install -g vercel
```

---

## 🔧 部署步骤

### 方式 1: 通过 GitHub 部署（推荐）✨

#### 步骤 1: 创建 GitHub 仓库
```bash
# 在项目根目录
git init
git add .
git commit -m "Initial commit"
```

#### 步骤 2: 推送到 GitHub
```bash
# 创建 GitHub 仓库后
git remote add origin https://github.com/YOUR_USERNAME/DAA_MVP.git
git branch -M main
git push -u origin main
```

#### 步骤 3: 在 Vercel 导入项目
1. 登录 Vercel: https://vercel.com
2. 点击 **"Add New..."** → **"Project"**
3. 选择 **"Import Git Repository"**
4. 找到您的 `DAA_MVP` 仓库并点击 **"Import"**
5. Vercel 会自动检测到这是一个 Python Flask 项目

#### 步骤 4: 配置环境变量
在 Vercel 项目设置中添加以下环境变量：

```
OPENAI_API_KEY=sk-guzlijsmobmunfkkeakmfkoovjgombjhryrkplnrhhcfwjoc
OPENAI_API_BASE=https://api.siliconflow.cn/v1
AI_MODEL=Qwen/Qwen3-Next-80B-A3B-Instruct
BASE_SEPOLIA_RPC=https://eth-sepolia.g.alchemy.com/v2/9tBXs__lxsUnksFJ2YEQ5
ALCHEMY_API_KEY=9tBXs__lxsUnksFJ2YEQ5
CONTRACT_ADDRESS=0xc184846f9a113b0a4bb81140b77c1dabb9e4c7e0
AGENT_PRIVATE_KEY=your_private_key_here
```

⚠️ **重要**: 不要在代码中直接写入私钥！

#### 步骤 5: 部署
点击 **"Deploy"** 按钮，Vercel 会自动构建和部署您的应用。

---

### 方式 2: 通过 Vercel CLI 部署

#### 步骤 1: 登录 Vercel
```bash
vercel login
```

#### 步骤 2: 部署
```bash
# 在项目根目录
vercel
```

按照提示完成配置：
- **Set up and deploy?** → Yes
- **Which scope?** → 选择您的账号
- **Link to existing project?** → No
- **What's your project's name?** → DAA_MVP（或自定义名称）
- **In which directory is your code located?** → ./

#### 步骤 3: 添加环境变量
```bash
vercel env add OPENAI_API_KEY
vercel env add OPENAI_API_BASE
vercel env add AI_MODEL
vercel env add BASE_SEPOLIA_RPC
vercel env add ALCHEMY_API_KEY
vercel env add CONTRACT_ADDRESS
# 注意：私钥建议不要添加到 Vercel，而是使用钱包连接方式
```

#### 步骤 4: 重新部署
```bash
vercel --prod
```

---

## ⚠️ 重要限制和注意事项

### 1. 超时限制
- **Hobby 计划**: 10 秒超时
- **Pro 计划**: 60 秒超时
- **AI 图片生成可能会超时**（通常需要 30-60 秒）

**解决方案**:
- 升级到 Pro 计划
- 或者将图片生成改为异步处理
- 或者使用更快的图片生成模型

### 2. 私钥安全
**强烈建议**: 在生产环境中不要使用后端代理铸造！

- 使用 **MetaMask 钱包连接** 功能让用户自己铸造
- 后端的 `/api/mint` 接口可以禁用

### 3. 数据库
Vercel 是 serverless 平台，没有持久化存储。如果需要：
- 使用 Vercel Postgres
- 使用外部数据库服务（如 MongoDB Atlas、Supabase）

### 4. 静态文件
所有静态文件（CSS、JS、图片）应该放在 `web/static/` 目录下

---

## 🔍 验证部署

部署成功后，您会获得一个 URL（类似 `https://daa-mvp.vercel.app`）

### 测试步骤:
1. 访问您的 Vercel URL
2. 输入一个故事进行 AI 评估
3. 如果评分 ≥ 85，尝试连接 MetaMask 铸造 NFT
4. 检查浏览器控制台是否有错误

---

## 📝 常见问题

### Q1: 部署后显示 "Internal Server Error"
**解决方案**:
- 检查 Vercel 日志: Project → Deployments → 点击部署 → Runtime Logs
- 确认所有环境变量已正确设置
- 检查 `requirements.txt` 中的依赖版本

### Q2: 图片生成超时
**解决方案**:
- 升级到 Vercel Pro 计划（60秒超时）
- 或修改代码，跳过图片生成步骤
- 或使用更快的 AI 模型

### Q3: 静态文件 404
**解决方案**:
- 确保文件在 `web/static/` 目录下
- 检查 `vercel.json` 中的路由配置

### Q4: 连接 MetaMask 失败
**解决方案**:
- 确认您的域名在 MetaMask 白名单中
- 检查浏览器控制台的错误信息
- 确保使用 HTTPS（Vercel 自动提供）

---

## 🔄 更新部署

### 通过 GitHub（自动部署）
```bash
git add .
git commit -m "Update message"
git push
```
Vercel 会自动检测到 push 并重新部署。

### 通过 CLI
```bash
vercel --prod
```

---

## 🎯 性能优化建议

1. **启用 Vercel Analytics**
   - 在 Vercel 项目设置中启用 Analytics
   - 监控应用性能和用户行为

2. **使用 CDN**
   - Vercel 自动将静态资源部署到全球 CDN
   - 确保图片和 CSS/JS 文件被正确缓存

3. **优化图片**
   - 压缩图片文件
   - 使用现代图片格式（WebP）

4. **异步处理**
   - 将耗时操作（如图片生成）改为后台任务
   - 使用 WebSocket 或轮询获取结果

---

## 🔗 有用的链接

- Vercel 文档: https://vercel.com/docs
- Vercel Python 支持: https://vercel.com/docs/runtimes#official-runtimes/python
- Vercel CLI 文档: https://vercel.com/docs/cli

---

## 🆘 获取帮助

如果遇到问题：
1. 查看 Vercel 部署日志
2. 检查浏览器控制台错误
3. 查阅 Vercel 官方文档
4. 在项目 GitHub Issues 中提问

---

祝您部署顺利！🎉

