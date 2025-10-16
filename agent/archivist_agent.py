"""
Digital Archivist Agent (DAA)
自主评估人文故事并在Base Sepolia测试网上铸造ERC-721 NFT
"""

import os
import json
from dotenv import load_dotenv
from web3 import Web3
from openai import OpenAI

# 加载环境变量
load_dotenv()

# ============== 配置区 ==============

# Base Sepolia 测试网 RPC URL
BASE_SEPOLIA_RPC = os.getenv("BASE_SEPOLIA_RPC", "https://sepolia.base.org")

# Agent 私钥（从环境变量加载）
AGENT_PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# 合约地址（部署后需要更新）
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0x0000000000000000000000000000000000000000")

# 合约 ABI（简化版，仅包含 mintToken 函数）
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "string", "name": "tokenURI", "type": "string"}
        ],
        "name": "mintToken",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# OpenAI API 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 元数据基础 URL（可以是 IPFS 或其他托管服务）
METADATA_BASE_URL = "https://ipfs.io/ipfs/"

# 评分阈值
SCORE_THRESHOLD = 85

# ============== 初始化 Web3 ==============

web3 = Web3(Web3.HTTPProvider(BASE_SEPOLIA_RPC))
print(f"🔗 连接到 Base Sepolia: {web3.is_connected()}")

# ============== AI 评估函数 ==============

def evaluate_story_with_ai(story_text: str) -> dict:
    """
    使用 OpenAI API 评估故事的价值
    
    Args:
        story_text: 待评估的故事文本
        
    Returns:
        dict: 包含 score, metadata_title, metadata_description 的字典
    """
    print("\n📝 开始 AI 评估...")
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
你是一位专业的文学评论家和文化档案管理员。请评估以下人文故事的价值，
并以 JSON 格式返回评估结果。

评分标准（0-100）：
- 情感深度和真实性 (30分)
- 文化和历史价值 (25分)
- 叙事质量和结构 (20分)
- 原创性和独特性 (15分)
- 社会意义和影响力 (10分)

故事内容：
{story_text}

请以严格的 JSON 格式返回（不要包含任何markdown格式）：
{{
    "score": [0-100的整数],
    "metadata_title": "[简短标题，最多50字符]",
    "metadata_description": "[详细描述，总结故事的核心价值和特点，100-200字符]"
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一位专业的文学评论家。请始终返回有效的JSON格式。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # 尝试清理可能的 markdown 格式
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        evaluation = json.loads(result_text.strip())
        
        print(f"✅ AI 评估完成:")
        print(f"   评分: {evaluation['score']}/100")
        print(f"   标题: {evaluation['metadata_title']}")
        print(f"   描述: {evaluation['metadata_description']}")
        
        return evaluation
        
    except Exception as e:
        print(f"❌ AI 评估失败: {str(e)}")
        raise


# ============== 链上铸造函数 ==============

def mint_memory_token(recipient_address: str, metadata: dict) -> str:
    """
    在 Base Sepolia 上铸造 MemoryToken NFT
    
    Args:
        recipient_address: 接收者地址
        metadata: 包含标题和描述的元数据字典
        
    Returns:
        str: 交易哈希
    """
    print("\n⛓️  准备链上铸造...")
    
    try:
        # 获取账户
        account = web3.eth.account.from_key(AGENT_PRIVATE_KEY)
        agent_address = account.address
        print(f"   Agent 地址: {agent_address}")
        
        # 创建合约实例
        contract = web3.eth.contract(
            address=Web3.to_checksum_address(CONTRACT_ADDRESS),
            abi=CONTRACT_ABI
        )
        
        # 构建元数据 JSON（简化版，实际应上传到 IPFS）
        token_metadata = {
            "name": metadata["metadata_title"],
            "description": metadata["metadata_description"],
            "image": "ipfs://QmExample",  # 占位符
            "attributes": [
                {
                    "trait_type": "Score",
                    "value": metadata["score"]
                },
                {
                    "trait_type": "Type",
                    "value": "Memory"
                }
            ]
        }
        
        # 在实际应用中，应该将 metadata 上传到 IPFS 并获取真实的 URI
        # 这里使用模拟的 URI
        token_uri = f"{METADATA_BASE_URL}Qm{metadata['score']}{metadata['metadata_title'][:10]}"
        
        print(f"   Token URI: {token_uri}")
        print(f"   接收者: {recipient_address}")
        
        # 构建交易
        nonce = web3.eth.get_transaction_count(agent_address)
        
        transaction = contract.functions.mintToken(
            Web3.to_checksum_address(recipient_address),
            token_uri
        ).build_transaction({
            'chainId': 84532,  # Base Sepolia Chain ID
            'gas': 300000,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce,
        })
        
        # 签名交易
        signed_txn = web3.eth.account.sign_transaction(transaction, AGENT_PRIVATE_KEY)
        
        # 发送交易
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_hash_hex = tx_hash.hex()
        
        print(f"   交易已发送: {tx_hash_hex}")
        print(f"   等待确认...")
        
        # 等待交易确认
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if tx_receipt['status'] == 1:
            print(f"✅ 铸造成功!")
            print(f"   Gas 使用: {tx_receipt['gasUsed']}")
            return tx_hash_hex
        else:
            print(f"❌ 交易失败")
            return None
            
    except Exception as e:
        print(f"❌ 铸造失败: {str(e)}")
        raise


# ============== 主运行函数 ==============

def run_archivist(story_text: str):
    """
    运行 Digital Archivist Agent 的完整流程
    
    Args:
        story_text: 待评估和归档的故事文本
    """
    print("=" * 60)
    print("🤖 Digital Archivist Agent (DAA) 启动")
    print("=" * 60)
    
    # 步骤 1: AI 评估
    try:
        evaluation = evaluate_story_with_ai(story_text)
    except Exception as e:
        print(f"\n❌ 流程中止: AI 评估失败 - {str(e)}")
        return
    
    # 步骤 2: 自主决策
    print(f"\n🤔 自主决策中...")
    score = evaluation["score"]
    
    if score >= SCORE_THRESHOLD:
        print(f"✅ 故事评分 {score} >= {SCORE_THRESHOLD}，符合归档标准！")
        print(f"🎯 决定：铸造 Memory Token NFT")
        
        # 步骤 3: 链上铸造
        try:
            # 获取 Agent 自己的地址作为接收者
            account = web3.eth.account.from_key(AGENT_PRIVATE_KEY)
            recipient = account.address
            
            tx_hash = mint_memory_token(recipient, evaluation)
            
            if tx_hash:
                print("\n" + "=" * 60)
                print("🎉 任务完成!")
                print("=" * 60)
                print(f"📊 AI 评估结果:")
                print(f"   评分: {evaluation['score']}/100")
                print(f"   标题: {evaluation['metadata_title']}")
                print(f"   描述: {evaluation['metadata_description']}")
                print(f"\n🔗 铸造成功:")
                print(f"   交易哈希: {tx_hash}")
                print(f"   浏览器: https://sepolia.basescan.org/tx/{tx_hash}")
                print("=" * 60)
        except Exception as e:
            print(f"\n❌ 流程中止: 铸造失败 - {str(e)}")
            return
    else:
        print(f"⚠️  故事评分 {score} < {SCORE_THRESHOLD}，未达到归档标准")
        print(f"🎯 决定：不铸造 NFT")
        print(f"\n💡 评估反馈:")
        print(f"   标题: {evaluation['metadata_title']}")
        print(f"   描述: {evaluation['metadata_description']}")


# ============== 测试示例 ==============

if __name__ == "__main__":
    # 示例故事文本
    sample_story = """
在一个古老的村庄里，住着一位年迈的制陶师傅。他用一生的时间，
将泥土塑造成器皿，也将记忆烧制进每一件作品。他的双手布满裂纹，
如同他捏制的陶罐表面的纹理。村里的年轻人都去了城市，只有他还守着
这门即将失传的手艺。

一个雨夜，他最后一次点燃了窑火。火光中，他看到了自己的一生——
童年时第一次触摸陶土的惊喜，青年时学艺的艰辛，以及晚年独自守望的
孤独。当第二天村民们发现他时，窑里的陶罐已经烧制完成，温润如玉。
而老人静静地坐在那里，脸上带着满足的笑容，仿佛他自己也成为了
他最后的作品。

这个故事传遍了整个地区，那件最后的陶罐被送进了博物馆。人们说，
如果你仔细聆听，还能听到陶罐里传来窑火燃烧的声音，那是一位匠人
对时光最温柔的诉说。
    """
    
    print("📖 测试故事:")
    print(sample_story)
    print("\n")
    
    # 运行 Agent
    run_archivist(sample_story)


