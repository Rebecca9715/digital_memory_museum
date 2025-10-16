# 🔧 Vercel 部署问题排查指南

## ✅ 我已经修复的问题

1. **移除了不必要的 agent 目录引用** - 减少依赖复杂度
2. **优化了 vercel.json 配置** - 增加内存和超时时间
3. **简化了导入路径** - 避免路径问题

---

## 🚨 当前的 500 错误可能原因

### 1️⃣ 环境变量未配置（最可能）

**问题**: Vercel 上的环境变量没有设置，导致应用启动失败。

**解决方案**: 在 Vercel 项目设置中添加以下环境变量：

```
OPENAI_API_KEY=sk-guzlijsmobmunfkkeakmfkoovjgombjhryrkplnrhhcfwjoc
OPENAI_API_BASE=https://api.siliconflow.cn/v1
AI_MODEL=Qwen/Qwen3-Next-80B-A3B-Instruct
BASE_SEPOLIA_RPC=https://eth-sepolia.g.alchemy.com/v2/9tBXs__lxsUnksFJ2YEQ5
ALCHEMY_API_KEY=9tBXs__lxsUnksFJ2YEQ5
CONTRACT_ADDRESS=0xc184846f9a113b0a4bb81140b77c1dabb9e4c7e0
```

**如何添加环境变量**:
1. 访问 https://vercel.com/dashboard
2. 选择您的项目 `digital_memory_museum`
3. 点击 **Settings** → **Environment Variables**
4. 逐个添加上述变量
5. 确保选择 **Production**, **Preview**, 和 **Development**
6. 点击 **Save**
7. 重新部署：**Deployments** → 最新部署 → **Redeploy**

---

### 2️⃣ 超时问题（图片生成）

**问题**: 
- Vercel Hobby 计划：10 秒超时
- AI 图片生成：通常需要 30-60 秒

**解决方案 A - 升级到 Pro（推荐）**:
- Vercel Pro: $20/月，60 秒超时
- 访问：https://vercel.com/account/billing

**解决方案 B - 禁用图片生成**:

修改 `web/app.py`，在图片生成部分添加超时保护：

```python
# 在 evaluate() 函数中
# 生成图片（如果有图片提示词）
image_url = None
if evaluation.get('image_prompt'):
    try:
        # 设置较短的超时时间
        image_url = generate_image(evaluation['image_prompt'])
        if image_url:
            evaluation['image_url'] = image_url
    except Exception as e:
        print(f"⚠️ 图片生成失败（预期）: {e}")
        evaluation['image_url'] = None  # 跳过图片
```

然后在 `generate_image()` 函数中：

```python
def generate_image(prompt):
    try:
        # ... existing code ...
        response = requests.post(url, headers=headers, json=payload, timeout=8)  # 8秒超时
        # ... rest of code ...
    except requests.Timeout:
        print("⏰ 图片生成超时，跳过")
        return None
    except Exception as e:
        print(f"图片生成错误: {e}")
        return None
```

---

### 3️⃣ Python 依赖问题

**问题**: 某些依赖在 Vercel 上安装失败。

**解决方案**: 确保 `requirements.txt` 在根目录且格式正确：

```txt
Flask==3.0.0
web3==6.11.1
openai==1.3.0
python-dotenv==1.0.0
flask-cors==4.0.0
requests==2.31.0
```

---

### 4️⃣ 检查 Vercel 日志

**如何查看详细日志**:

1. 访问 https://vercel.com/dashboard
2. 选择您的项目
3. 点击 **Deployments**
4. 选择最新的部署
5. 点击 **Function Logs** 或 **Runtime Logs**
6. 查看错误信息

**常见错误信息**:

```
ModuleNotFoundError: No module named 'xxx'
→ 依赖未安装，检查 requirements.txt

KeyError: 'OPENAI_API_KEY'
→ 环境变量未设置

Timeout
→ 函数执行超时（需要升级或优化代码）
```

---

## 📋 完整部署检查清单

### ✅ 步骤 1: 环境变量
- [ ] `OPENAI_API_KEY` 已设置
- [ ] `OPENAI_API_BASE` 已设置
- [ ] `AI_MODEL` 已设置
- [ ] `BASE_SEPOLIA_RPC` 已设置
- [ ] `ALCHEMY_API_KEY` 已设置
- [ ] `CONTRACT_ADDRESS` 已设置
- [ ] 所有变量在 Production、Preview、Development 环境都已添加

### ✅ 步骤 2: 代码检查
- [ ] `requirements.txt` 在根目录
- [ ] `vercel.json` 配置正确
- [ ] GitHub 仓库代码已更新（git push 成功）

### ✅ 步骤 3: 重新部署
- [ ] 在 Vercel Dashboard → Deployments → Redeploy
- [ ] 等待 2-3 分钟
- [ ] 检查日志是否有错误

### ✅ 步骤 4: 测试
- [ ] 访问 Vercel URL
- [ ] 尝试打开主页
- [ ] 测试 AI 评估功能（可能超时）
- [ ] 测试 MetaMask 钱包连接

---

## 🎯 推荐配置（避免超时）

### 选项 1: 升级 Vercel Pro ✨
**优点**:
- 60 秒超时（足够 AI 图片生成）
- 更多资源和性能
- 适合生产环境

**价格**: $20/月

### 选项 2: 禁用图片生成 💡
**优点**:
- 完全免费（Hobby 计划）
- 响应速度快
- 仍然可以铸造 NFT（只是没有图片）

**实现**: 见上面的"解决方案 B"

### 选项 3: 使用外部服务器 🖥️
**优点**:
- 没有超时限制
- 完全控制

**缺点**:
- 需要自己管理服务器
- 可能有额外成本

**推荐平台**:
- Railway: https://railway.app
- Render: https://render.com
- 自己的 VPS

---

## 🔍 调试技巧

### 1. 本地测试 Vercel 配置
```bash
# 安装 Vercel CLI
npm install -g vercel

# 本地模拟 Vercel 环境
vercel dev
```

### 2. 查看实时日志
```bash
# 实时查看 Vercel 日志
vercel logs <deployment-url> --follow
```

### 3. 测试单个接口
```bash
# 测试状态接口
curl https://your-app.vercel.app/api/status

# 测试评估接口（会超时）
curl -X POST https://your-app.vercel.app/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{"story_text":"测试故事"}'
```

---

## 📞 需要帮助？

如果问题仍然存在：

1. **查看 Vercel 日志** - 最重要的诊断工具
2. **检查环境变量** - 90% 的问题都是这个
3. **尝试本地 vercel dev** - 排除配置问题
4. **考虑升级 Pro 或禁用图片生成** - 解决超时问题

---

## 🎉 预期结果

**环境变量配置后**:
- ✅ 主页正常加载
- ✅ AI 评估功能工作（15-30 秒）
- ⚠️ AI 图片生成可能超时（需要 Pro 或禁用）
- ✅ MetaMask 钱包连接正常
- ✅ NFT 铸造功能可用

**升级 Pro 或禁用图片后**:
- ✅ 所有功能完全正常
- ✅ 响应时间合理
- ✅ 生产环境可用

