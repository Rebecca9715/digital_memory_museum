// Web3 Wallet Connection and NFT Minting Functions

// Global Web3 State
window.web3State = {
    isConnected: false,
    account: null,
    chainId: null,
    contract: null,
    web3: null
};

// Contract configuration (will be fetched from server)
let CONTRACT_ADDRESS = null;
let CONTRACT_ABI = null;
const SEPOLIA_CHAIN_ID = '0xaa36a7'; // 11155111 in hexadecimal

// Initialize Web3
async function initWeb3() {
    console.log('🔧 Initializing Web3...');
    
    // Check if MetaMask is installed
    if (typeof window.ethereum === 'undefined') {
        showNotification('Please install MetaMask wallet!', 'error');
        return false;
    }

    try {
        // Load contract configuration
        await loadContractConfig();
        
        // Listen for account changes
        window.ethereum.on('accountsChanged', handleAccountsChanged);
        
        // Listen for chain changes
        window.ethereum.on('chainChanged', handleChainChanged);
        
        console.log('✅ Web3 initialized');
        return true;
    } catch (error) {
        console.error('Web3 initialization failed:', error);
        return false;
    }
}

// Load contract configuration
async function loadContractConfig() {
    try {
        const response = await fetch('/api/contract-config');
        const config = await response.json();
        
        CONTRACT_ADDRESS = config.address;
        CONTRACT_ABI = config.abi;
        
        console.log('📝 Contract address:', CONTRACT_ADDRESS);
    } catch (error) {
        console.error('Failed to load contract config:', error);
        // Use default ABI
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

// Connect wallet
async function connectWallet() {
    console.log('🔐 Connecting wallet...');
    
    if (typeof window.ethereum === 'undefined') {
        showNotification('❌ MetaMask not detected, please install first!', 'error');
        window.open('https://metamask.io/download/', '_blank');
        return false;
    }

    try {
        // Request account access
        const accounts = await window.ethereum.request({ 
            method: 'eth_requestAccounts' 
        });
        
        if (accounts.length === 0) {
            showNotification('No account found', 'warning');
            return false;
        }

        // Get chain ID
        const chainId = await window.ethereum.request({ 
            method: 'eth_chainId' 
        });

        // Update state
        window.web3State.account = accounts[0];
        window.web3State.chainId = chainId;
        window.web3State.isConnected = true;

        // Check if on Sepolia network
        if (chainId !== SEPOLIA_CHAIN_ID) {
            await switchToSepolia();
        } else {
            initContract();
        }

        // Update UI
        updateWalletUI();
        
        showNotification(`✅ Wallet connected: ${formatAddress(accounts[0])}`, 'success');
        console.log('✅ Wallet connected successfully:', accounts[0]);
        
        return true;
    } catch (error) {
        console.error('Failed to connect wallet:', error);
        showNotification('Failed to connect wallet: ' + error.message, 'error');
        return false;
    }
}

// Switch to Sepolia network
async function switchToSepolia() {
    try {
        await window.ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: SEPOLIA_CHAIN_ID }],
        });
        
        showNotification('✅ Switched to Sepolia testnet', 'success');
        initContract();
    } catch (error) {
        // If network doesn't exist, add it
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
                showNotification('Failed to add Sepolia network', 'error');
            }
        } else {
            showNotification('Failed to switch network: ' + error.message, 'error');
        }
    }
}

// Initialize contract
function initContract() {
    if (!window.ethereum || !CONTRACT_ADDRESS) {
        console.warn('Cannot initialize contract: missing ethereum or contract address');
        return;
    }

    try {
        window.web3State.web3 = new Web3(window.ethereum);
        window.web3State.contract = new window.web3State.web3.eth.Contract(
            CONTRACT_ABI,
            CONTRACT_ADDRESS
        );
        console.log('✅ Contract initialized');
    } catch (error) {
        console.error('Failed to initialize contract:', error);
    }
}

// Mint NFT with wallet
async function mintNFTWithWallet(metadata) {
    if (!window.web3State.isConnected) {
        showNotification('Please connect wallet first', 'warning');
        const connected = await connectWallet();
        if (!connected) return null;
    }

    if (!window.web3State.contract) {
        showNotification('Contract not initialized', 'error');
        return null;
    }

    try {
        // Build NFT standard metadata
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
        
        // If there's an image prompt, add it to attributes
        if (metadata.image_prompt) {
            nftMetadata.attributes.push({
                trait_type: 'Image Prompt',
                value: metadata.image_prompt
            });
        }
        
        // Convert metadata to base64 encoded data URI
        const metadataJson = JSON.stringify(nftMetadata);
        const metadataBase64 = btoa(unescape(encodeURIComponent(metadataJson)));
        const tokenURI = `data:application/json;base64,${metadataBase64}`;

        console.log('🎨 Starting to mint NFT...');
        console.log('📝 NFT metadata:', nftMetadata);
        console.log('🔗 Token URI length:', tokenURI.length, 'characters');

        // Call contract's mint function
        const tx = await window.web3State.contract.methods
            .mint(tokenURI)
            .send({ 
                from: window.web3State.account,
                value: '0' // Free minting
            });

        console.log('✅ Minting successful! Transaction hash:', tx.transactionHash);

        return {
            success: true,
            tx_hash: tx.transactionHash,
            gas_used: tx.gasUsed,
            block_number: tx.blockNumber,
            explorer_url: `https://sepolia.etherscan.io/tx/${tx.transactionHash}`,
            from: window.web3State.account
        };

    } catch (error) {
        console.error('Minting failed:', error);
        
        let errorMessage = 'Minting failed';
        if (error.code === 4001) {
            errorMessage = 'User cancelled transaction';
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        throw new Error(errorMessage);
    }
}

// Disconnect wallet
function disconnectWallet() {
    window.web3State.isConnected = false;
    window.web3State.account = null;
    window.web3State.chainId = null;
    window.web3State.contract = null;
    
    updateWalletUI();
    showNotification('Wallet disconnected', 'info');
}

// Handle account changes
function handleAccountsChanged(accounts) {
    if (accounts.length === 0) {
        disconnectWallet();
    } else if (accounts[0] !== window.web3State.account) {
        window.web3State.account = accounts[0];
        updateWalletUI();
        showNotification(`Account switched: ${formatAddress(accounts[0])}`, 'info');
    }
}

// Handle chain changes
function handleChainChanged(chainId) {
    window.web3State.chainId = chainId;
    
    if (chainId !== SEPOLIA_CHAIN_ID) {
        showNotification('⚠️ Please switch to Sepolia testnet', 'warning');
    } else {
        initContract();
        showNotification('✅ Connected to Sepolia testnet', 'success');
    }
    
    updateWalletUI();
}

// Update wallet UI
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
                <span>🔗 ${window.web3State.chainId === SEPOLIA_CHAIN_ID ? 'Sepolia' : 'Wrong Network'}</span>
            `;
        }
    } else {
        walletBtn.textContent = '🔐 Connect Wallet';
        walletBtn.classList.remove('connected');
        
        if (walletInfo) {
            walletInfo.style.display = 'none';
        }
    }
}

// Format address
function formatAddress(address) {
    if (!address) return '';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Delay initialization to wait for Web3 library to load
    setTimeout(initWeb3, 100);
});

// Export functions for global use
window.web3Wallet = {
    connect: connectWallet,
    disconnect: disconnectWallet,
    mintNFT: mintNFTWithWallet,
    isConnected: () => window.web3State.isConnected,
    getAccount: () => window.web3State.account
};

console.log('✅ Web3 wallet module loaded');

