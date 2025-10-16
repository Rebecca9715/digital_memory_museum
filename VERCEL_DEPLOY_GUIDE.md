# 🚀 Vercel 部署完整指南

## ✅ 我已经修复的问题

### 1. **添加了 Vercel 入口点** (`api/index.py`)
- 创建了专门的 WSGI 入口点，让 Vercel 能正确调用 Flask 应用
- 解决了路径问题

### 2. **增强了错误处理**
- Web3 初始化添加了 try-catch，防止网络问题导致应用崩溃
- 环境变量缺失时会打印警告而不是崩溃

### 3. **启用了 CORS 支持**
- 添加了 `flask-cors` 导入和初始化
- 确保前端可以正常调用 API

### 4. **移除了硬编码密钥**
- 改为完全依赖环境变量
- 更安全，符合生产环境最佳实践

### 5. **优化了 Vercel 配置**
- 增加内存到 3008 MB（最大值）
- 设置 60 秒超时（Pro 计划需要）
- 优化路由配置

---

## 🔧 现在需要您做的：配置环境变量

### 步骤 1: 访问 Vercel Dashboard

1. 打开 https://vercel.com/dashboard
2. 选择您的项目 `digital_memory_museum`
3. 点击顶部的 **Settings** 标签

### 步骤 2: 添加环境变量

在 **Settings** → **Environment Variables** 页面，添加以下 **6 个** 变量：

#### ✨ 必需的环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `OPENAI_API_KEY` | `sk-guzlijsmobmunfkkeakmfkoovjgombjhryrkplnrhhcfwjoc` | 硅基流动 API 密钥 |
| `OPENAI_API_BASE` | `https://api.siliconflow.cn/v1` | 硅基流动 API 地址 |
| `AI_MODEL` | `Qwen/Qwen3-Next-80B-A3B-Instruct` | AI 模型名称 |
| `ALCHEMY_API_KEY` | `9tBXs__lxsUnksFJ2YEQ5` | Alchemy API 密钥 |
| `CONTRACT_ADDRESS` | `0xc184846f9a113b0a4bb81140b77c1dabb9e4c7e0` | 您部署的 NFT 合约地址 |
| `SCORE_THRESHOLD` | `85` | NFT 铸造评分阈值 |

#### ⚠️ 重要提示：

每个变量添加时，**必须勾选全部三个选项**：
- ✅ Production
- ✅ Preview
- ✅ Development

### 步骤 3: 重新部署

1. 点击顶部的 **Deployments** 标签
2. 找到最新的部署
3. 点击右侧的 **"..."** 菜单
4. 选择 **Redeploy**
5. 确认重新部署

**等待 2-3 分钟**，让 Vercel 完成部署。

---

## 📊 检查部署状态

### 查看构建日志

1. 在 **Deployments** 页面，点击最新的部署
2. 查看 **Building** 日志：
   - ✅ 应该看到 "Installing dependencies..."
   - ✅ 应该看到 "Build completed"
   
### 查看函数日志

1. 点击 **Functions** 标签
2. 点击 `api/index.py` 函数
3. 点击 **Function Logs**
4. 应该看到：
   ```
   ✅ Web3 初始化成功，连接到: https://eth-sepolia.g.alchemy.com/v2/...
   ```

### 如果看到警告

如果看到：
```
⚠️  警告: OPENAI_API_KEY 环境变量未设置
⚠️  警告: ALCHEMY_API_KEY 环境变量未设置
```

**说明环境变量没配置好**，请回到步骤 2 重新检查。

---

## 🎯 预期结果

### ✅ 成功的标志：

1. **主页加载**：访问您的 Vercel URL，应该看到漂亮的界面
2. **系统状态**：主页显示"系统正常运行"
3. **示例故事**：侧边栏显示示例故事
4. **AI 评估**：输入故事后，15-30 秒内返回评估结果
5. **钱包连接**：点击"Connect Wallet"可以连接 MetaMask

### ⚠️ 已知限制：

#### 免费计划 (Hobby) 限制：

- ⏰ **函数超时**: 10 秒
- 🎨 **AI 图片生成**: 需要 30-60 秒，**会超时**
- 💰 **解决方案**:
  - 升级到 Pro ($20/月) → 60 秒超时
  - 或者禁用图片生成（我可以帮您修改）

#### Pro 计划优势：

- ⏰ 60 秒函数超时（足够图片生成）
- 🚀 更快的冷启动
- 📊 更多资源
- 🎯 适合生产环境

---

## 🐛 常见问题排查

### 1. 500 错误持续出现

**检查清单**：
- [ ] 所有 6 个环境变量都添加了吗？
- [ ] 每个变量都勾选了 Production/Preview/Development 吗？
- [ ] 重新部署了吗？
- [ ] 查看了函数日志吗？

**解决方案**：
```bash
# 在 Vercel Dashboard 的 Function Logs 中查看具体错误
# 如果看到 ModuleNotFoundError，说明依赖问题
# 如果看到 KeyError，说明环境变量问题
```

### 2. AI 评估超时

**症状**：前端显示"请求超时"或 504 错误

**原因**：
- Hobby 计划：10 秒超时
- AI API 响应慢（15-30 秒）
- AI 图片生成需要 30-60 秒

**解决方案 A - 升级 Pro**：
```
访问 https://vercel.com/account/billing
选择 Pro 计划 ($20/月)
```

**解决方案 B - 禁用图片生成**（我可以帮您）：
```python
# 修改代码，跳过图片生成步骤
# 评估仍然正常，只是 NFT 没有图片
```

### 3. 图片生成总是失败

**症状**：评估成功，但没有图片显示

**原因**：
- Hobby 计划超时
- 图片 API 限流

**解决方案**：
- 升级到 Pro 计划
- 或接受没有图片（功能仍可用）

### 4. Web3 连接失败

**症状**：系统状态显示"Web3 未连接"

**原因**：
- `ALCHEMY_API_KEY` 未设置或错误

**解决方案**：
```bash
# 在 Vercel Environment Variables 中检查：
ALCHEMY_API_KEY=9tBXs__lxsUnksFJ2YEQ5

# 确保没有多余空格，没有引号
```

---

## 📋 完整检查清单

在报告问题前，请完成以下检查：

### ✅ 环境变量配置
- [ ] `OPENAI_API_KEY` ✓
- [ ] `OPENAI_API_BASE` ✓
- [ ] `AI_MODEL` ✓
- [ ] `ALCHEMY_API_KEY` ✓
- [ ] `CONTRACT_ADDRESS` ✓
- [ ] `SCORE_THRESHOLD` ✓
- [ ] 所有变量都勾选了 Production ✓
- [ ] 所有变量都勾选了 Preview ✓
- [ ] 所有变量都勾选了 Development ✓

### ✅ 部署状态
- [ ] 最新代码已推送到 GitHub
- [ ] Vercel 已重新部署
- [ ] 构建日志显示"Build completed"
- [ ] 没有构建错误

### ✅ 功能测试
- [ ] 主页可以访问
- [ ] 系统状态正常
- [ ] 可以看到示例故事
- [ ] AI 评估可以工作（可能慢）
- [ ] 钱包连接可以工作

---

## 🎉 成功后的样子

访问您的 Vercel URL（类似 `https://digital-memory-museum.vercel.app`），您应该看到：

1. **美观的主页**：渐变背景，动画效果
2. **系统状态**：右上角显示"✅ 正常运行"
3. **示例故事**：右侧栏有 3 个示例
4. **输入框**：可以输入故事
5. **评估按钮**："🔍 开始评估"按钮
6. **钱包按钮**："Connect Wallet"按钮

**测试流程**：
1. 点击示例故事之一
2. 点击"开始评估"
3. 等待 15-30 秒（会看到加载动画）
4. 看到评分、反馈、建议
5. 如果评分 ≥ 85，可以铸造 NFT
6. 连接 MetaMask，确认铸造

---

## 💰 关于费用

### Hobby 计划（免费）：
- ✅ 可以部署应用
- ✅ 主要功能可用
- ⚠️  AI 评估可能慢
- ❌ AI 图片生成会超时

### Pro 计划（$20/月）：
- ✅ 所有功能完全可用
- ✅ 60 秒超时（足够图片生成）
- ✅ 更快的响应速度
- ✅ 适合生产环境

**我的建议**：
- 如果只是测试：使用 Hobby 计划，接受没有图片
- 如果要正式使用：升级 Pro 计划

---

## 🆘 需要帮助？

### 如果部署仍然失败：

1. **截图发给我**：
   - Vercel 环境变量页面
   - Function Logs 中的错误信息
   - 浏览器中的错误（按 F12 查看控制台）

2. **提供以下信息**：
   - Vercel 部署 URL
   - 错误发生的具体步骤
   - 是否是 Hobby 或 Pro 计划

3. **我可以帮您**：
   - 调试具体错误
   - 优化配置
   - 禁用图片生成（如果需要）
   - 推荐其他部署方案

---

## 🌟 下一步

部署成功后，您可以：

1. **分享 URL**：把 Vercel URL 分享给朋友测试
2. **自定义域名**：在 Vercel Settings → Domains 添加自己的域名
3. **监控使用**：在 Vercel Analytics 查看访问情况
4. **持续开发**：本地修改 → git push → Vercel 自动部署

恭喜您完成部署！🎉

