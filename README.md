# 🏛️ Digital Memory Museum (DMM) | 数字记忆博物馆

一个结合 AI 评估和区块链技术的创新项目，让珍贵的人文故事和记忆永久保存在链上。

**在线体验：** [https://digital-memory-museum.vercel.app](https://digital-memory-museum.vercel.app)

---

## 📋 项目简介

**Digital Memory Museum (DMM) | 数字记忆博物馆** 是一个 Web3 + AI 的创新应用，旨在：

- 🤖 **AI 智能评估**：使用先进的 AI 模型（Qwen）评估人文故事的价值
- 🎨 **AI 图像生成**：为每个珍贵记忆生成独特的视觉化图像
- ⛓️ **链上永久保存**：将高价值的记忆铸造为 NFT，永久保存在区块链上
- 💎 **用户自主铸造**：用户可以通过 MetaMask 钱包自主铸造属于自己的记忆 NFT

## ✨ 核心功能

### 1. 📝 故事提交与评估
- 用户提交个人记忆、人文故事
- AI 从多个维度评估故事价值（情感深度、文化价值、叙事质量等）
- 实时显示评分和详细评语

### 2. 🎨 AI 图像生成
- 根据故事内容自动生成独特的视觉化图像
- 使用 SiliconFlow 图像生成 API
- 每个记忆都有专属的艺术呈现

### 3. ⛓️ NFT 铸造
- **钱包连接**：支持 MetaMask 连接
- **用户自主铸造**：评分达标后，用户可自行铸造 NFT
- **完整元数据**：包含故事标题、描述、AI 生成图像、评分等
- **Base Sepolia 测试网**：安全、低成本的测试环境

### 4. 💻 现代化 Web 界面
- 响应式设计，支持移动端和桌面端
- 美观的渐变色 UI
- 实时状态更新和交互反馈
- 内置示例故事库

## 🏗️ 技术架构

```
Digital-Memory-Museum/
├── web/                    # Flask Web 应用
│   ├── app.py             # 主应用逻辑
│   ├── static/            # 静态资源
│   │   ├── css/          # 样式文件
│   │   └── js/           # JavaScript 文件
│   └── templates/         # HTML 模板
├── contracts/             # Solidity 智能合约
│   ├── MemoryToken.sol   # ERC-721 NFT 合约
│   └── MemoryToken_ABI.json
├── api/                   # Vercel Serverless Functions
│   └── index.py          # Vercel 入口点
├── vercel.json           # Vercel 部署配置
└── requirements.txt      # Python 依赖
```

## 🚀 快速开始

### 在线体验（推荐）

直接访问：[https://digital-memory-museum.vercel.app](https://digital-memory-museum.vercel.app)

1. 输入你的故事或选择示例
2. 点击"开始评估"
3. 查看 AI 评分和生成的图像
4. 如果评分达标（≥85分），点击"连接钱包"
5. 确认交易，铸造你的记忆 NFT

### 本地运行

#### 1. 克隆项目

```bash
git clone https://github.com/Rebecca9715/digital_memory_museum.git
cd digital_memory_museum
```

#### 2. 配置环境变量

```bash
cp env.example .env
```

编辑 `.env` 文件，填写以下内容：

```env
# AI 配置（使用 SiliconFlow API）
OPENAI_API_KEY=your_siliconflow_api_key
OPENAI_API_BASE=https://api.siliconflow.cn/v1
AI_MODEL=Qwen/Qwen3-Next-80B-A3B-Instruct

# 区块链配置
ALCHEMY_API_KEY=your_alchemy_api_key
CONTRACT_ADDRESS=your_deployed_contract_address

# 评分阈值（可选，默认 85）
SCORE_THRESHOLD=85
```

#### 3. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 4. 启动服务器

```bash
cd web
python app.py
```

访问 `http://localhost:5001`

## 🔧 部署智能合约

### 使用 Remix IDE（推荐）

详细步骤请参考：[部署合约步骤.md](./部署合约步骤.md)

简要步骤：
1. 访问 [Remix IDE](https://remix.ethereum.org/)
2. 复制 `contracts/MemoryToken.sol` 到 Remix
3. 编译合约（Solidity ^0.8.20）
4. 连接 MetaMask 到 Base Sepolia 测试网
5. 部署合约
6. 复制合约地址到 `.env` 的 `CONTRACT_ADDRESS`

### 获取测试币

- **Base Sepolia 测试币**：[Base Sepolia Faucet](https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet)

## 🎯 AI 评估标准（满分 100）

| 维度 | 分数 | 说明 |
|-----|------|-----|
| **情感深度和真实性** | 30分 | 故事的情感共鸣和真实感 |
| **文化和历史价值** | 25分 | 对文化传承和历史记录的贡献 |
| **叙事质量和结构** | 20分 | 故事的完整性和表达能力 |
| **原创性和独特性** | 15分 | 故事的独特视角和创新性 |
| **社会意义和影响力** | 10分 | 对社会的启发和影响 |

**铸造阈值**：评分 ≥ 85 分的故事可以铸造为 NFT

## 💻 技术栈

### 前端
- HTML5 / CSS3 / JavaScript
- Web3.js（MetaMask 集成）
- 响应式设计

### 后端
- Python 3.9+
- Flask Web 框架
- OpenAI API（SiliconFlow 兼容）

### 区块链
- Solidity ^0.8.20
- OpenZeppelin ERC721
- Base Sepolia Testnet
- Alchemy RPC

### 部署
- Vercel（前端 + Serverless Functions）
- GitHub（代码托管和 CI/CD）

## 📊 智能合约 API

### 核心功能

#### `mint(string memory tokenURI) public payable`
用户自主铸造 NFT

**参数**：
- `tokenURI`: NFT 元数据 URI（包含图像、描述等）

**返回**：
- `tokenId`: 新铸造的 Token ID

#### `getCurrentTokenId() public view`
获取下一个将铸造的 Token ID

#### `tokensOfOwner(address owner) public view`
查询某地址拥有的所有 Token ID

## 🔐 安全提示

⚠️ **重要事项**：

1. **不要泄露私钥**：永远不要在代码中硬编码私钥
2. **使用测试网**：当前项目使用 Base Sepolia 测试网
3. **环境变量**：所有敏感信息通过 `.env` 管理
4. **合约权限**：合约部署后，建议转移所有权或使用多签
5. **API 密钥**：定期轮换 API 密钥

## 🌐 Vercel 部署

项目已配置自动部署到 Vercel。每次推送到 `main` 分支都会自动触发部署。

### 手动部署

```bash
# 推送到 GitHub
git push origin main

# Vercel 会自动检测并部署
```

### 配置环境变量

在 Vercel Dashboard → Settings → Environment Variables 中配置：
- `OPENAI_API_KEY`
- `OPENAI_API_BASE`
- `AI_MODEL`
- `ALCHEMY_API_KEY`
- `CONTRACT_ADDRESS`
- `SCORE_THRESHOLD`

## 📱 使用场景

- 📖 **个人回忆录**：保存珍贵的家庭故事和个人经历
- 🌏 **文化传承**：记录传统习俗、方言、民间故事
- 🏛️ **口述历史**：永久保存历史见证者的叙述
- 💝 **情感寄托**：纪念重要的人、事、物
- 🎨 **创意写作**：展示和保护原创文学作品

## 🗺️ 项目路线图

### ✅ 已完成（V1.0）
- [x] AI 故事评估
- [x] AI 图像生成
- [x] MetaMask 钱包集成
- [x] 用户自主 NFT 铸造
- [x] Web 界面
- [x] Vercel 在线部署
- [x] Base Sepolia 测试网集成

### 🔜 计划中（V2.0）
- [ ] IPFS 存储完整故事内容
- [ ] 多链部署（Ethereum、Polygon、Arbitrum）
- [ ] NFT 交易市场
- [ ] 社区投票和策展
- [ ] 多语言支持（英语、日语等）
- [ ] 主网部署

## 🤝 贡献

欢迎所有形式的贡献！

- 🐛 提交 Bug 报告
- 💡 提出新功能建议
- 🔧 提交 Pull Request
- 📖 改进文档

## 📄 开源协议

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- **在线演示**：[https://digital-memory-museum.vercel.app](https://digital-memory-museum.vercel.app)
- **GitHub 仓库**：[https://github.com/Rebecca9715/digital_memory_museum](https://github.com/Rebecca9715/digital_memory_museum)
- **Base Sepolia 浏览器**：[https://sepolia.basescan.org/](https://sepolia.basescan.org/)
- **SiliconFlow API**：[https://siliconflow.cn](https://siliconflow.cn)
- **Alchemy**：[https://www.alchemy.com/](https://www.alchemy.com/)

## 💬 联系方式

有任何问题或建议？欢迎通过以下方式联系：

- GitHub Issues: [提交 Issue](https://github.com/Rebecca9715/digital_memory_museum/issues)
- Email: [你的邮箱]

---

<div align="center">

**🏛️ 让每一份珍贵的记忆都值得被永久保存 🏛️**

*Built with ❤️ for the future of digital memory preservation*

</div>
