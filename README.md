# 🤖 Digital Archivist Agent (DAA)

一个自主的 AI Agent，能够评估人文故事的价值，并自动在 Base Sepolia 测试网上铸造 ERC-721 "MemoryToken" NFT。

## 📋 项目概述

Digital Archivist Agent (DAA) 是一个 Web3 + AI 的创新项目，它结合了：
- **AI 评估**：使用 GPT-4 评估故事的文学和文化价值
- **自主决策**：基于评分自动决定是否归档
- **链上铸造**：在 Base Sepolia 测试网上铸造 NFT 以永久保存有价值的故事

## 🏗️ 项目结构

```
DAA_MVP/
├── contracts/              # Solidity 智能合约
│   └── MemoryToken.sol    # ERC-721 NFT 合约
├── agent/                 # Python Agent 脚本
│   ├── archivist_agent.py # 核心 Agent 逻辑
│   └── requirements.txt   # Python 依赖
├── .env.example           # 环境变量示例
└── README.md             # 项目文档
```

## 🚀 快速开始

### 🌐 方法 A: Web 界面（推荐）

**3 步启动 Web 界面：**

```bash
# 1. 配置环境变量
cp env.example .env
# 编辑 .env 文件，填写 PRIVATE_KEY, OPENAI_API_KEY, CONTRACT_ADDRESS

# 2. 安装依赖
cd web
pip install -r requirements.txt

# 3. 启动服务器
python app.py
# 访问 http://localhost:5000
```

### 💻 方法 B: 命令行

#### 安装 Python 依赖

```bash
cd DAA_MVP/agent
pip install -r requirements.txt
```

#### 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填写：
# - PRIVATE_KEY: 你的钱包私钥
# - OPENAI_API_KEY: OpenAI API 密钥
# - CONTRACT_ADDRESS: 部署后的合约地址
```

### 2. 部署智能合约

#### 使用 Remix IDE（推荐新手）

1. 访问 [Remix IDE](https://remix.ethereum.org/)
2. 创建新文件 `MemoryToken.sol`，复制 `contracts/MemoryToken.sol` 的内容
3. 安装 OpenZeppelin 插件或导入：
   ```solidity
   // 使用 Remix 的 GitHub 导入功能
   ```
4. 编译合约（Solidity 版本：^0.8.20）
5. 切换到 "Deploy & Run Transactions"
6. 选择 "Injected Provider - MetaMask"
7. 确保 MetaMask 连接到 **Base Sepolia 测试网**
8. 部署合约
9. 复制合约地址到 `.env` 文件的 `CONTRACT_ADDRESS`

#### 使用 Hardhat/Foundry（推荐开发者）

```bash
# 如需使用 Hardhat 或 Foundry，请自行配置部署脚本
```

### 3. 获取测试网代币

访问 [Base Sepolia Faucet](https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet) 获取测试 ETH。

### 4. 运行 Agent

**Web 界面（推荐）：**
```bash
cd web
python app.py
# 在浏览器中访问 http://localhost:5000
```

**命令行：**
```bash
cd agent
python archivist_agent.py
```

Agent 将：
1. 📝 使用 AI 评估内置的示例故事
2. 🤔 根据评分自主决策是否铸造 NFT
3. ⛓️ 如果评分 ≥ 85，自动在链上铸造 MemoryToken

### 🎨 Web 界面功能

- ✨ 美观的现代化 UI
- 📝 文本编辑器输入故事
- 🤖 实时 AI 评估和反馈
- 📊 可视化评分展示
- ⛓️ 一键铸造 NFT
- 📚 内置示例故事
- 💰 实时钱包余额显示

## 📖 使用示例

### 评估自定义故事

修改 `archivist_agent.py` 底部的 `sample_story` 变量：

```python
custom_story = """
你的故事内容...
"""

run_archivist(custom_story)
```

### 调整评分阈值

在 `archivist_agent.py` 中修改：

```python
SCORE_THRESHOLD = 85  # 修改为你想要的阈值（0-100）
```

## 🧠 工作原理

### AI 评估标准（0-100 分）

- **情感深度和真实性** (30分)
- **文化和历史价值** (25分)
- **叙事质量和结构** (20分)
- **原创性和独特性** (15分)
- **社会意义和影响力** (10分)

### 决策逻辑

```
评分 ≥ 85 → 铸造 NFT ✅
评分 < 85 → 不铸造 ❌
```

### NFT 元数据

每个 MemoryToken 包含：
- **name**: 故事标题
- **description**: 故事评估描述
- **score**: AI 评分
- **type**: Memory

## 🔧 技术栈

### 智能合约
- Solidity ^0.8.20
- OpenZeppelin ERC721
- Base Sepolia Testnet

### Python Agent
- `web3.py` - 以太坊交互
- `openai` - GPT-4 API
- `python-dotenv` - 环境变量管理

## 📝 智能合约 API

### `mintToken(address recipient, string memory tokenURI)`

铸造新的 MemoryToken NFT（仅合约所有者可调用）

**参数：**
- `recipient`: 接收者地址
- `tokenURI`: Token 元数据 URI

**返回：**
- `tokenId`: 新铸造的 Token ID

### `getCurrentTokenId()`

获取当前 Token 计数（下一个将铸造的 Token ID）

## 🔐 安全注意事项

⚠️ **重要提醒：**

1. **永远不要提交 `.env` 文件到 Git**
2. **私钥仅用于测试网，不要使用主网私钥**
3. **定期轮换 API 密钥**
4. **在生产环境中使用硬件钱包或 KMS**

## 🛣️ 路线图

### MVP (当前版本)
- [x] AI 评估故事价值
- [x] 自主决策铸造
- [x] Base Sepolia 链上铸造

### 未来功能
- [ ] IPFS 集成，存储完整故事和元数据
- [ ] Web UI 界面
- [ ] 多语言支持
- [ ] 社区投票机制
- [ ] 主网部署
- [ ] DAO 治理

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [Base Sepolia 浏览器](https://sepolia.basescan.org/)
- [Base 官方文档](https://docs.base.org/)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Web3.py 文档](https://web3py.readthedocs.io/)

## 💡 灵感

这个项目探索了 AI 与 Web3 的结合，展示了 AI Agent 如何自主与区块链交互，
为数字内容的价值评估和永久保存提供了新的可能性。

---

**Built with ❤️ for the future of digital archiving**


