# 🎨 NFT 铸造使用指南

## 🎉 新功能：连接钱包铸造 NFT！

您的 Digital Archivist Agent 现在支持两种铸造方式：

1. **用户钱包铸造**（推荐） - 使用您自己的 MetaMask 钱包
2. **后端铸造** - 使用服务器端配置的私钥

---

## 📋 部署步骤

### 1. 部署智能合约到 Sepolia 测试网

#### 使用 Remix IDE（最简单）

1. **打开 Remix IDE**: https://remix.ethereum.org/

2. **创建新文件**: 
   - 点击 "File Explorers"
   - 创建文件 `MemoryToken.sol`
   - 复制 `contracts/MemoryToken.sol` 的内容到文件中

3. **编译合约**:
   - 点击左侧 "Solidity Compiler"
   - 选择编译器版本 `0.8.20` 或更高
   - 点击 "Compile MemoryToken.sol"

4. **部署合约**:
   - 点击左侧 "Deploy & Run Transactions"
   - Environment 选择 "Injected Provider - MetaMask"
   - 在 MetaMask 中确保已连接到 **Sepolia 测试网**
   - 点击 "Deploy" 按钮
   - 在 MetaMask 中确认交易

5. **复制合约地址**:
   - 部署成功后，在 "Deployed Contracts" 下找到您的合约
   - 点击复制按钮，复制合约地址

### 2. 配置环境变量

编辑 `.env` 文件：

```bash
nano /Users/rebeccawang/web3/dda/DAA_MVP/.env
```

更新以下内容：

```bash
# 合约地址（替换为您部署的合约地址）
CONTRACT_ADDRESS=0x您部署的合约地址

# 如果要使用后端铸造，需要配置私钥（可选）
PRIVATE_KEY=您的MetaMask私钥（不包含0x）

# Alchemy API Key（已配置）
ALCHEMY_API_KEY=9tBXs__lxsUnksFJ2YEQ5
```

### 3. 获取 Sepolia 测试币

访问以下水龙头获取免费测试币：

- **Alchemy Sepolia Faucet**: https://sepoliafaucet.com/
- **Infura Faucet**: https://www.infura.io/faucet/sepolia
- **QuickNode Faucet**: https://faucet.quicknode.com/ethereum/sepolia

需要至少 **0.01 ETH** 用于铸造交易。

---

## 🎮 使用方法

### 方式 1: 使用 MetaMask 钱包铸造（推荐）

1. **安装 MetaMask**:
   - 如果还没有安装，访问 https://metamask.io/download/
   - 安装浏览器扩展

2. **切换到 Sepolia 网络**:
   - 打开 MetaMask
   - 点击顶部的网络选择器
   - 选择 "Sepolia 测试网络"

3. **访问网站**:
   - 打开 http://localhost:5001
   - 页面加载后会自动初始化 Web3

4. **连接钱包**:
   - 点击右上角的 "🔐 连接钱包" 按钮
   - MetaMask 会弹出授权请求
   - 点击 "连接" 授权网站访问您的钱包
   - 连接成功后按钮会显示您的钱包地址

5. **评估故事**:
   - 输入或选择一个示例故事
   - 点击 "🧠 AI 评估"
   - 等待评估结果

6. **铸造 NFT**:
   - 如果评分 ≥ 85，会显示 "🎨 铸造 NFT" 按钮
   - 点击按钮
   - MetaMask 会弹出交易确认窗口
   - 检查 Gas 费用
   - 点击 "确认" 发送交易
   - 等待交易确认（约 10-30 秒）
   - 铸造成功后可以查看交易详情

### 方式 2: 使用后端铸造

如果您配置了 `PRIVATE_KEY` 环境变量：

1. **不连接钱包**，直接使用网站
2. 评估故事后，点击 "🎨 铸造 NFT"
3. 后端会使用配置的私钥自动铸造
4. 无需支付 Gas 费（由后端支付）

---

## 🔍 智能合约功能

### 公开函数

#### `mint(string tokenURI)` - 用户铸造
- **参数**: tokenURI - NFT 元数据
- **返回**: tokenId - 新铸造的 NFT ID
- **费用**: 免费（mintPrice = 0）
- **权限**: 任何人都可以调用

#### `mintToken(address recipient, string tokenURI)` - 管理员铸造
- **参数**: 
  - recipient - 接收地址
  - tokenURI - NFT 元数据
- **返回**: tokenId
- **权限**: 仅合约所有者

#### `tokensOfOwner(address owner)` - 查询用户NFT
- **参数**: owner - 钱包地址
- **返回**: tokenId 数组
- **权限**: 任何人可查询

---

## 📊 查看您的 NFT

### 在区块浏览器查看

1. 铸造成功后，点击 "🔗 在区块浏览器中查看" 链接
2. 可以看到交易详情和 NFT 信息

### 在 MetaMask 查看

1. 打开 MetaMask
2. 切换到 "NFTs" 标签
3. 可能需要手动导入 NFT：
   - 点击 "Import NFTs"
   - 输入合约地址
   - 输入 Token ID（从铸造结果中获取）

### 在 OpenSea 测试网查看

1. 访问 https://testnets.opensea.io/
2. 连接您的钱包
3. 查看 "Profile" 中的 NFT

---

## 🛠️ 高级配置

### 修改铸造价格

合约所有者可以设置铸造价格：

```solidity
// 在 Remix 中调用
setMintPrice(1000000000000000) // 0.001 ETH (以 wei 为单位)
```

### 禁用公开铸造

```solidity
setPublicMintEnabled(false) // 禁用
setPublicMintEnabled(true)  // 启用
```

---

## ❓ 常见问题

### Q: 为什么点击"连接钱包"没反应？

A: 
- 检查是否安装了 MetaMask
- 刷新页面重试
- 检查浏览器控制台是否有错误

### Q: MetaMask 提示"错误的网络"怎么办？

A: 
- 在 MetaMask 中手动切换到 Sepolia 测试网
- 或者点击 MetaMask 弹窗中的"切换网络"按钮

### Q: 铸造时提示"余额不足"？

A: 
- 访问水龙头获取测试币
- 需要至少 0.01 ETH 用于 Gas 费

### Q: 如何查看我铸造的所有 NFT？

A: 
- 在 MetaMask 的 NFTs 标签中查看
- 访问 https://testnets.opensea.io/ 查看
- 使用区块浏览器搜索您的地址

### Q: 可以在主网上使用吗？

A: 
- 当前配置为 Sepolia 测试网
- 主网部署需要修改配置并支付真实 ETH
- **不建议在测试阶段使用主网**

---

## 🎨 元数据说明

每个铸造的 NFT 包含：

```json
{
  "name": "故事标题",
  "description": "AI 评估描述",
  "score": 92,
  "timestamp": "2025-10-15T23:00:00"
}
```

未来可以扩展为：
- 上传故事内容到 IPFS
- 添加封面图片
- 包含评估的详细反馈

---

## 🚀 下一步优化

- [ ] 集成 IPFS 存储完整故事
- [ ] 添加 NFT 封面图生成
- [ ] 支持批量铸造
- [ ] 添加白名单功能
- [ ] 部署到主网

---

**祝您铸造愉快！** 🎉

有问题随时询问！

