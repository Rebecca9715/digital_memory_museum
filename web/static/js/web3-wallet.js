// Web3 钱包连接和NFT铸造功能

// 全局 Web3 状态
window.web3State = {
    isConnected: false,
    account: null,
    chainId: null,
    contract: null,
    web3: null
};

// 合约配置（将从服务器获取）
let CONTRACT_ADDRESS = null;
let CONTRACT_ABI = null;
const SEPOLIA_CHAIN_ID = '0xaa36a7'; // 11155111 的十六进制

// 初始化 Web3
async function initWeb3() {
    console.log('🔧 初始化 Web3...');
    
    // 检查是否安装 MetaMask
    if (typeof window.ethereum === 'undefined') {
        showNotification('请安装 MetaMask 钱包！', 'error');
        return false;
    }

    try {
        // 获取合约配置
        await loadContractConfig();
        
        // 监听账户变化
        window.ethereum.on('accountsChanged', handleAccountsChanged);
        
        // 监听链变化
        window.ethereum.on('chainChanged', handleChainChanged);
        
        console.log('✅ Web3 初始化完成');
        return true;
    } catch (error) {
        console.error('Web3 初始化失败:', error);
        return false;
    }
}

// 加载合约配置
async function loadContractConfig() {
    try {
        const response = await fetch('/api/contract-config');
        const config = await response.json();
        
        CONTRACT_ADDRESS = config.address;
        CONTRACT_ABI = config.abi;
        
        console.log('📝 合约地址:', CONTRACT_ADDRESS);
    } catch (error) {
        console.error('加载合约配置失败:', error);
        // 使用默认 ABI
        CONTRACT_ABI = [
            {
                "inputs": [{"internalType": "string", "name": "tokenURI", "type": "string"}],
                "name": "mint",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "payable",
                "type": "function"
            }
        ];
    }
}

// 连接钱包
async function connectWallet() {
    console.log('🔐 正在连接钱包...');
    
    if (typeof window.ethereum === 'undefined') {
        showNotification('❌ 未检测到 MetaMask，请先安装！', 'error');
        window.open('https://metamask.io/download/', '_blank');
        return false;
    }

    try {
        // 请求账户访问
        const accounts = await window.ethereum.request({ 
            method: 'eth_requestAccounts' 
        });
        
        if (accounts.length === 0) {
            showNotification('未找到账户', 'warning');
            return false;
        }

        // 获取链 ID
        const chainId = await window.ethereum.request({ 
            method: 'eth_chainId' 
        });

        // 更新状态
        window.web3State.account = accounts[0];
        window.web3State.chainId = chainId;
        window.web3State.isConnected = true;

        // 检查是否在 Sepolia 网络
        if (chainId !== SEPOLIA_CHAIN_ID) {
            await switchToSepolia();
        } else {
            initContract();
        }

        // 更新 UI
        updateWalletUI();
        
        showNotification(`✅ 钱包已连接: ${formatAddress(accounts[0])}`, 'success');
        console.log('✅ 钱包连接成功:', accounts[0]);
        
        return true;
    } catch (error) {
        console.error('连接钱包失败:', error);
        showNotification('连接钱包失败: ' + error.message, 'error');
        return false;
    }
}

// 切换到 Sepolia 网络
async function switchToSepolia() {
    try {
        await window.ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: SEPOLIA_CHAIN_ID }],
        });
        
        showNotification('✅ 已切换到 Sepolia 测试网', 'success');
        initContract();
    } catch (error) {
        // 如果网络不存在，添加它
        if (error.code === 4902) {
            try {
                await window.ethereum.request({
                    method: 'wallet_addEthereumChain',
                    params: [{
                        chainId: SEPOLIA_CHAIN_ID,
                        chainName: 'Sepolia Test Network',
                        nativeCurrency: {
                            name: 'SepoliaETH',
                            symbol: 'ETH',
                            decimals: 18
                        },
                        rpcUrls: ['https://sepolia.infura.io/v3/'],
                        blockExplorerUrls: ['https://sepolia.etherscan.io']
                    }]
                });
                initContract();
            } catch (addError) {
                showNotification('添加 Sepolia 网络失败', 'error');
            }
        } else {
            showNotification('切换网络失败: ' + error.message, 'error');
        }
    }
}

// 初始化合约
function initContract() {
    if (!window.ethereum || !CONTRACT_ADDRESS) {
        console.warn('无法初始化合约：缺少 ethereum 或合约地址');
        return;
    }

    try {
        window.web3State.web3 = new Web3(window.ethereum);
        window.web3State.contract = new window.web3State.web3.eth.Contract(
            CONTRACT_ABI,
            CONTRACT_ADDRESS
        );
        console.log('✅ 合约已初始化');
    } catch (error) {
        console.error('初始化合约失败:', error);
    }
}

// 使用钱包铸造 NFT
async function mintNFTWithWallet(metadata) {
    if (!window.web3State.isConnected) {
        showNotification('请先连接钱包', 'warning');
        const connected = await connectWallet();
        if (!connected) return null;
    }

    if (!window.web3State.contract) {
        showNotification('合约未初始化', 'error');
        return null;
    }

    try {
        // 构建符合 NFT 标准的元数据
        const nftMetadata = {
            name: metadata.metadata_title || 'Untitled Memory',
            description: metadata.metadata_description || '',
            image: metadata.image_url || '',
            attributes: [
                {
                    trait_type: 'Score',
                    value: metadata.score || 0
                },
                {
                    trait_type: 'Timestamp',
                    value: metadata.timestamp || ''
                }
            ]
        };
        
        // 如果有图片提示词，也加入属性
        if (metadata.image_prompt) {
            nftMetadata.attributes.push({
                trait_type: 'Image Prompt',
                value: metadata.image_prompt
            });
        }
        
        // 将元数据转换为 base64 编码的 data URI
        const metadataJson = JSON.stringify(nftMetadata);
        const metadataBase64 = btoa(unescape(encodeURIComponent(metadataJson)));
        const tokenURI = `data:application/json;base64,${metadataBase64}`;

        console.log('🎨 开始铸造 NFT...');
        console.log('📝 NFT 元数据:', nftMetadata);
        console.log('🔗 Token URI 长度:', tokenURI.length, '字符');

        // 调用合约的 mint 函数
        const tx = await window.web3State.contract.methods
            .mint(tokenURI)
            .send({ 
                from: window.web3State.account,
                value: '0' // 免费铸造
            });

        console.log('✅ 铸造成功！交易哈希:', tx.transactionHash);

        return {
            success: true,
            tx_hash: tx.transactionHash,
            gas_used: tx.gasUsed,
            block_number: tx.blockNumber,
            explorer_url: `https://sepolia.etherscan.io/tx/${tx.transactionHash}`,
            from: window.web3State.account
        };

    } catch (error) {
        console.error('铸造失败:', error);
        
        let errorMessage = '铸造失败';
        if (error.code === 4001) {
            errorMessage = '用户取消了交易';
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        throw new Error(errorMessage);
    }
}

// 断开钱包
function disconnectWallet() {
    window.web3State.isConnected = false;
    window.web3State.account = null;
    window.web3State.chainId = null;
    window.web3State.contract = null;
    
    updateWalletUI();
    showNotification('钱包已断开连接', 'info');
}

// 处理账户变化
function handleAccountsChanged(accounts) {
    if (accounts.length === 0) {
        disconnectWallet();
    } else if (accounts[0] !== window.web3State.account) {
        window.web3State.account = accounts[0];
        updateWalletUI();
        showNotification(`账户已切换: ${formatAddress(accounts[0])}`, 'info');
    }
}

// 处理链变化
function handleChainChanged(chainId) {
    window.web3State.chainId = chainId;
    
    if (chainId !== SEPOLIA_CHAIN_ID) {
        showNotification('⚠️ 请切换到 Sepolia 测试网', 'warning');
    } else {
        initContract();
        showNotification('✅ 已连接到 Sepolia 测试网', 'success');
    }
    
    updateWalletUI();
}

// 更新钱包 UI
function updateWalletUI() {
    const walletBtn = document.getElementById('walletConnectBtn');
    const walletInfo = document.getElementById('walletInfo');
    
    if (!walletBtn) return;

    if (window.web3State.isConnected && window.web3State.account) {
        walletBtn.textContent = formatAddress(window.web3State.account);
        walletBtn.classList.add('connected');
        
        if (walletInfo) {
            walletInfo.style.display = 'block';
            walletInfo.innerHTML = `
                <span>🔗 ${window.web3State.chainId === SEPOLIA_CHAIN_ID ? 'Sepolia' : '错误网络'}</span>
            `;
        }
    } else {
        walletBtn.textContent = '🔐 连接钱包';
        walletBtn.classList.remove('connected');
        
        if (walletInfo) {
            walletInfo.style.display = 'none';
        }
    }
}

// 格式化地址
function formatAddress(address) {
    if (!address) return '';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    // 延迟初始化，等待 Web3 库加载
    setTimeout(initWeb3, 100);
});

// 导出函数供全局使用
window.web3Wallet = {
    connect: connectWallet,
    disconnect: disconnectWallet,
    mintNFT: mintNFTWithWallet,
    isConnected: () => window.web3State.isConnected,
    getAccount: () => window.web3State.account
};

console.log('✅ Web3 钱包模块已加载');

