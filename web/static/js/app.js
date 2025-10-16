// Digital Memory Museum (DMM) | 数字记忆博物馆 - 前端 JavaScript

// 全局状态
let currentEvaluation = null;
let exampleStories = [];

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏛️ Digital Memory Museum 已加载');
    checkStatus();
    loadExamples();
    setupEventListeners();
});

// 设置事件监听器
function setupEventListeners() {
    // 绑定按钮事件
    const evaluateBtn = document.getElementById('evaluateBtn');
    const clearBtn = document.getElementById('clearBtn');
    const mintBtn = document.getElementById('mintBtn');
    
    if (evaluateBtn) {
        evaluateBtn.addEventListener('click', evaluateStory);
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', clearInput);
    }
    
    if (mintBtn) {
        mintBtn.addEventListener('click', mintNFT);
    }
    
    // 自动保存输入
    const storyInput = document.getElementById('storyInput');
    if (storyInput) {
        storyInput.addEventListener('input', debounce(function() {
            localStorage.setItem('daa_draft', storyInput.value);
        }, 500));
        
        // 恢复草稿
        const draft = localStorage.getItem('daa_draft');
        if (draft && !storyInput.value) {
            storyInput.value = draft;
        }
    }
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 检查系统状态
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        updateStatusUI(data);
        
        // 定期检查（每30秒）
        setTimeout(checkStatus, 30000);
    } catch (error) {
        console.error('Status check failed:', error);
        updateStatusUI({ error: true });
    }
}

// 更新状态 UI
function updateStatusUI(data) {
    const indicator = document.getElementById('connectionStatus');
    const text = document.getElementById('connectionText');
    const balance = document.getElementById('balanceText');
    
    if (data.error || !data.web3_connected) {
        indicator.classList.add('error');
        text.textContent = '❌ 连接失败';
        showNotification('无法连接到 Base Sepolia', 'error');
    } else {
        indicator.classList.remove('error');
        text.innerHTML = `✅ Base Sepolia <span style="opacity: 0.8;">(Chain ${data.chain_id})</span>`;
        
        if (data.balance !== undefined) {
            const balanceValue = parseFloat(data.balance);
            const balanceColor = balanceValue < 0.001 ? '#f59e0b' : '#22c55e';
            balance.innerHTML = `💰 余额: <span style="color: ${balanceColor}; font-weight: 600;">${balanceValue.toFixed(4)} ETH</span>`;
            
            if (balanceValue < 0.001) {
                showNotification('余额不足，建议充值测试 ETH', 'warning');
            }
        }
    }
}

// 加载示例故事
async function loadExamples() {
    try {
        const response = await fetch('/api/examples');
        exampleStories = await response.json();
        
        const container = document.getElementById('exampleStories');
        if (container) {
            container.innerHTML = exampleStories.map((story, index) => `
                <div class="example-card" onclick="loadExample(${index})" data-index="${index}">
                    <h3>${escapeHtml(story.title)}</h3>
                    <p>${escapeHtml(story.content.substring(0, 100))}...</p>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load examples:', error);
    }
}

// 加载示例到输入框
function loadExample(index) {
    const story = exampleStories[index];
    const input = document.getElementById('storyInput');
    
    if (input && story) {
        input.value = story.content;
        input.focus();
        
        // 平滑滚动到输入框
        input.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // 高亮选中的示例
        document.querySelectorAll('.example-card').forEach(card => {
            card.style.borderColor = 'transparent';
        });
        document.querySelector(`[data-index="${index}"]`).style.borderColor = 'var(--primary-color)';
        
        showNotification(`已加载示例: ${story.title}`, 'success');
    }
}

// 清空输入
function clearInput() {
    const input = document.getElementById('storyInput');
    if (input) {
        input.value = '';
        localStorage.removeItem('daa_draft');
    }
    
    hideResults();
    currentEvaluation = null;
    
    // 移除示例高亮
    document.querySelectorAll('.example-card').forEach(card => {
        card.style.borderColor = 'transparent';
    });
    
    showNotification('已清空内容', 'success');
}

// 评估故事
async function evaluateStory() {
    const storyText = document.getElementById('storyInput').value.trim();
    
    // 验证输入
    if (!storyText) {
        showNotification('请先输入故事内容！', 'error');
        return;
    }

    if (storyText.length < 50) {
        showNotification('故事内容太短，至少需要 50 个字符！', 'warning');
        return;
    }

    // 显示加载状态
    showLoading();
    disableButtons(true);

    try {
        const startTime = Date.now();
        
        // 创建带超时的 fetch
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000); // 120秒超时
        
        const response = await fetch('/api/evaluate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ story_text: storyText }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);
        
        const data = await response.json();
        const duration = ((Date.now() - startTime) / 1000).toFixed(1);

        if (!response.ok) {
            throw new Error(data.error || '评估失败');
        }

        currentEvaluation = data;
        displayResults(data);
        
        showNotification(`✅ 评估完成！用时 ${duration} 秒`, 'success');

    } catch (error) {
        console.error('Evaluation error:', error);
        
        let errorMessage = '评估失败';
        if (error.name === 'AbortError') {
            errorMessage = '请求超时，请稍后重试';
        } else if (error.message === 'Failed to fetch') {
            errorMessage = '网络连接失败，请检查服务器是否运行';
        } else {
            errorMessage = error.message;
        }
        
        showNotification('❌ ' + errorMessage, 'error');
        hideResults();
    } finally {
        hideLoading();
        disableButtons(false);
    }
}

// 显示评估结果
function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const emptyState = document.getElementById('emptyState');
    
    if (resultsSection) resultsSection.style.display = 'block';
    if (emptyState) emptyState.style.display = 'none';
    
    // 显示评分（带动画）
    const scoreDisplay = document.getElementById('scoreDisplay');
    if (scoreDisplay) {
        animateScore(scoreDisplay, 0, data.score, 1000);
    }
    
    // 状态文本
    const statusText = data.should_mint ? 
        '✅ 达到归档标准！' : 
        '⚠️ 未达到归档标准';
    const scoreStatus = document.getElementById('scoreStatus');
    if (scoreStatus) {
        scoreStatus.textContent = statusText;
        scoreStatus.style.color = data.should_mint ? 'var(--success-color)' : 'var(--warning-color)';
    }

    // 显示详情
    updateElement('resultTitle', data.metadata_title);
    updateElement('resultDescription', data.metadata_description);
    updateElement('resultFeedback', data.feedback || '暂无详细反馈');
    
    // 显示图片（如果有）
    displayGeneratedImage(data.image_url, data.image_prompt);

    // 显示/隐藏铸造区域
    updateMintSection(data);
    
    // 滚动到结果
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 显示生成的图片
function displayGeneratedImage(imageUrl, imagePrompt) {
    const imageContainer = document.getElementById('generatedImageContainer');
    if (!imageContainer) return;
    
    if (imageUrl) {
        imageContainer.innerHTML = `
            <div class="generated-image-wrapper">
                <h4>🎨 AI 生成的 NFT 图片</h4>
                <img src="${escapeHtml(imageUrl)}" alt="Generated NFT Image" class="generated-image">
                ${imagePrompt ? `<p class="image-prompt"><strong>图片提示词:</strong> ${escapeHtml(imagePrompt)}</p>` : ''}
            </div>
        `;
        imageContainer.style.display = 'block';
    } else {
        imageContainer.style.display = 'none';
        imageContainer.innerHTML = '';
    }
}

// 更新铸造区域
function updateMintSection(data) {
    const mintSection = document.getElementById('mintSection');
    const mintMessage = document.getElementById('mintMessage');
    const mintBtn = document.getElementById('mintBtn');
    
    if (!mintSection) return;
    
    mintSection.style.display = 'block';
    
    if (data.should_mint) {
        mintSection.classList.remove('warning');
        if (mintMessage) {
            mintMessage.innerHTML = `
                🎉 <strong>恭喜！</strong>这个故事达到了归档标准（评分: ${data.score}/100）！
                <br><br>
                您可以将其铸造为 NFT，永久保存在区块链上。
            `;
        }
        if (mintBtn) {
            mintBtn.style.display = 'block';
            mintBtn.disabled = false;
        }
    } else {
        mintSection.classList.add('warning');
        if (mintMessage) {
            mintMessage.innerHTML = `
                📝 这个故事暂未达到归档标准（评分: ${data.score}/100 < 阈值 85）。
                <br><br>
                <strong>建议：</strong>${data.feedback ? data.feedback.substring(0, 150) + '...' : '改进后重新提交'}
            `;
        }
        if (mintBtn) {
            mintBtn.style.display = 'none';
        }
    }
    
    // 清空之前的铸造结果
    const mintResult = document.getElementById('mintResult');
    if (mintResult) mintResult.innerHTML = '';
}

// 铸造 NFT
async function mintNFT() {
    if (!currentEvaluation || !currentEvaluation.should_mint) {
        showNotification('当前故事未达到铸造标准！', 'error');
        return;
    }

    const mintBtn = document.getElementById('mintBtn');
    const originalText = mintBtn.textContent;
    
    mintBtn.disabled = true;
    mintBtn.textContent = '⏳ 铸造中...';

    const resultDiv = document.getElementById('mintResult');
    resultDiv.innerHTML = `
        <div class="loading active">
            <div class="spinner"></div>
            <p>正在发送交易到区块链...<br><small>这可能需要 10-30 秒</small></p>
        </div>
    `;

    try {
        const startTime = Date.now();
        let data;

        // 检查是否连接了钱包
        if (window.web3Wallet && window.web3Wallet.isConnected()) {
            // 使用钱包铸造
            console.log('🔐 使用连接的钱包铸造 NFT...');
            data = await window.web3Wallet.mintNFT(currentEvaluation);
        } else {
            // 使用后端铸造
            console.log('🖥️ 使用后端铸造 NFT...');
            const response = await fetch('/api/mint', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ metadata: currentEvaluation })
            });

            data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || '铸造失败');
            }
        }

        const duration = ((Date.now() - startTime) / 1000).toFixed(1);

        if (data && data.success !== false) {
            const walletUsed = window.web3Wallet && window.web3Wallet.isConnected();
            
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h4>🎉 铸造成功！</h4>
                    ${walletUsed ? `<p><strong>铸造方式:</strong> 用户钱包 (${window.web3Wallet.getAccount().substring(0,10)}...)</p>` : ''}
                    <p><strong>交易哈希:</strong><br><code style="font-size: 0.9em;">${data.tx_hash}</code></p>
                    <p><strong>Gas 使用:</strong> ${data.gas_used.toLocaleString()} units</p>
                    <p><strong>区块高度:</strong> #${data.block_number}</p>
                    <p><strong>用时:</strong> ${duration} 秒</p>
                    <a href="${data.explorer_url}" target="_blank" class="tx-link">
                        🔗 在区块浏览器中查看
                    </a>
                </div>
            `;
            
            mintBtn.style.display = 'none';
            showNotification('🎉 NFT 铸造成功！', 'success');
            
            // 清除草稿
            localStorage.removeItem('daa_draft');
            
        } else {
            throw new Error('交易执行失败');
        }

    } catch (error) {
        console.error('Mint error:', error);
        resultDiv.innerHTML = `
            <div class="alert alert-error">
                <h4>❌ 铸造失败</h4>
                <p>${escapeHtml(error.message)}</p>
                <p><small>提示：您可以连接 MetaMask 钱包自己铸造 NFT</small></p>
            </div>
        `;
        
        mintBtn.disabled = false;
        mintBtn.textContent = originalText;
        
        showNotification('铸造失败: ' + error.message, 'error');
    }
}

// UI 辅助函数
function showLoading() {
    const loading = document.getElementById('loadingSection');
    const results = document.getElementById('resultsSection');
    const empty = document.getElementById('emptyState');
    
    if (loading) loading.classList.add('active');
    if (results) results.style.display = 'none';
    if (empty) empty.style.display = 'none';
}

function hideLoading() {
    const loading = document.getElementById('loadingSection');
    if (loading) loading.classList.remove('active');
}

function hideResults() {
    const results = document.getElementById('resultsSection');
    const empty = document.getElementById('emptyState');
    
    if (results) results.style.display = 'none';
    if (empty) empty.style.display = 'block';
}

function disableButtons(disabled) {
    const buttons = ['evaluateBtn', 'clearBtn', 'mintBtn'];
    buttons.forEach(id => {
        const btn = document.getElementById(id);
        if (btn) btn.disabled = disabled;
    });
}

function updateElement(id, content) {
    const element = document.getElementById(id);
    if (element) element.textContent = content;
}

// 分数动画
function animateScore(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 16);
}

// 通知系统
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // 样式
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 20px',
        borderRadius: '10px',
        color: 'white',
        fontWeight: '600',
        zIndex: '9999',
        boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
        animation: 'slideInRight 0.3s ease',
        maxWidth: '400px'
    });
    
    // 根据类型设置背景色
    const colors = {
        success: '#22c55e',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    notification.style.background = colors[type] || colors.info;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// HTML 转义（防止 XSS）
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 添加必要的 CSS 动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// 导出供全局使用
window.DAA = {
    evaluateStory,
    mintNFT,
    loadExample,
    clearInput,
    checkStatus
};

console.log('✅ Digital Memory Museum 初始化完成');



