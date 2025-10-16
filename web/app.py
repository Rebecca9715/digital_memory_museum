"""
Digital Archivist Agent - Web 界面
基于 Flask 的简单 Web 应用
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
import json
import requests
from datetime import datetime

# 添加 agent 目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agent'))

from dotenv import load_dotenv
from web3 import Web3
from openai import OpenAI

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)

# ============== 配置 ==============

# Alchemy API 配置
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY", "9tBXs__lxsUnksFJ2YEQ5")
SEPOLIA_RPC = f"https://eth-sepolia.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

# 区块链配置
AGENT_PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0x0000000000000000000000000000000000000000")

# AI 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-guzlijsmobmunfkkeakmfkoovjgombjhryrkplnrhhcfwjoc")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.siliconflow.cn/v1")
AI_MODEL = os.getenv("AI_MODEL", "Qwen/Qwen3-Next-80B-A3B-Instruct")
SCORE_THRESHOLD = int(os.getenv("SCORE_THRESHOLD", "85"))

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

# 初始化 Web3 - 连接到 Ethereum Sepolia 测试网
web3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC))

# ============== 路由 ==============

@app.route('/')
def index():
    """主页"""
    return render_template('index.html', threshold=SCORE_THRESHOLD)


@app.route('/api/status')
def status():
    """检查系统状态"""
    try:
        is_connected = web3.is_connected()
        
        status_data = {
            "web3_connected": is_connected,
            "contract_address": CONTRACT_ADDRESS,
            "threshold": SCORE_THRESHOLD
        }
        
        if is_connected:
            status_data["chain_id"] = web3.eth.chain_id
            status_data["block_number"] = web3.eth.block_number
            
            # 检查钱包
            if AGENT_PRIVATE_KEY and AGENT_PRIVATE_KEY != "your_private_key_here":
                try:
                    account = web3.eth.account.from_key(AGENT_PRIVATE_KEY)
                    balance = web3.eth.get_balance(account.address)
                    status_data["agent_address"] = account.address
                    status_data["balance"] = float(web3.from_wei(balance, 'ether'))
                except Exception as e:
                    status_data["wallet_error"] = "私钥配置无效"
        
        return jsonify(status_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_image(prompt):
    """调用 SiliconFlow API 生成图片"""
    try:
        url = "https://api.siliconflow.cn/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "black-forest-labs/FLUX.1-schnell",
            "prompt": prompt,
            "image_size": "1024x1024",
            "batch_size": 1,
            "num_inference_steps": 20
        }
        
        print(f"🎨 生成图片，提示词: {prompt}")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        if result.get('images') and len(result['images']) > 0:
            image_url = result['images'][0]['url']
            print(f"✅ 图片生成成功: {image_url}")
            return image_url
        else:
            print("❌ 图片生成失败: 没有返回图片URL")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ 图片生成超时")
        return None
    except Exception as e:
        print(f"❌ 图片生成失败: {str(e)}")
        return None


@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    """评估故事"""
    try:
        data = request.json
        story_text = data.get('story_text', '').strip()
        
        if not story_text:
            return jsonify({"error": "故事内容不能为空"}), 400
        
        if len(story_text) < 50:
            return jsonify({"error": "故事内容太短，至少需要 50 个字符"}), 400
        
        # AI 评估 - 使用硅基流动 API
        client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE
        )
        
        prompt = f"""你是一位专业的文学评论家和文化档案管理员。请评估以下人文故事的价值，
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
    "metadata_description": "[详细描述，总结故事的核心价值和特点，100-200字符]",
    "feedback": "[详细的评估反馈，说明评分理由]",
    "image_prompt": "[英文图片生成提示词，描述故事的核心场景、氛围和视觉元素，适合用于AI绘画，50-100字符]"
}}"""
        
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "你是一位专业的文学评论家。请始终返回有效的JSON格式。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # 清理可能的 markdown 格式
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        evaluation = json.loads(result_text.strip())
        evaluation['timestamp'] = datetime.now().isoformat()
        evaluation['should_mint'] = evaluation['score'] >= SCORE_THRESHOLD
        
        # 生成图片（如果有图片提示词）
        image_url = None
        if evaluation.get('image_prompt'):
            image_url = generate_image(evaluation['image_prompt'])
            if image_url:
                evaluation['image_url'] = image_url
                print(f"✅ NFT 图片已生成: {image_url}")
            else:
                print("⚠️  图片生成失败，但评估继续进行")
                evaluation['image_url'] = None
        
        return jsonify(evaluation)
        
    except json.JSONDecodeError as e:
        return jsonify({"error": f"AI 响应解析失败: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"评估失败: {str(e)}"}), 500


@app.route('/api/mint', methods=['POST'])
def mint():
    """铸造 NFT"""
    try:
        data = request.json
        metadata = data.get('metadata', {})
        
        if not metadata.get('metadata_title') or not metadata.get('metadata_description'):
            return jsonify({"error": "元数据不完整"}), 400
        
        # 获取账户
        account = web3.eth.account.from_key(AGENT_PRIVATE_KEY)
        agent_address = account.address
        
        # 创建合约实例
        contract = web3.eth.contract(
            address=Web3.to_checksum_address(CONTRACT_ADDRESS),
            abi=CONTRACT_ABI
        )
        
        # 构建符合 NFT 标准的元数据
        nft_metadata = {
            "name": metadata.get('metadata_title', 'Untitled Memory'),
            "description": metadata.get('metadata_description', ''),
            "image": metadata.get('image_url', ''),
            "attributes": [
                {
                    "trait_type": "Score",
                    "value": metadata.get('score', 0)
                },
                {
                    "trait_type": "Timestamp",
                    "value": metadata.get('timestamp', '')
                }
            ]
        }
        
        # 如果有图片提示词，也加入属性
        if metadata.get('image_prompt'):
            nft_metadata['attributes'].append({
                "trait_type": "Image Prompt",
                "value": metadata.get('image_prompt', '')
            })
        
        # 将元数据转换为 base64 编码的 data URI
        import base64
        metadata_json = json.dumps(nft_metadata, ensure_ascii=False)
        metadata_base64 = base64.b64encode(metadata_json.encode('utf-8')).decode('utf-8')
        token_uri = f"data:application/json;base64,{metadata_base64}"
        
        print(f"📝 NFT 元数据: {json.dumps(nft_metadata, ensure_ascii=False, indent=2)}")
        print(f"🔗 Token URI 长度: {len(token_uri)} 字符")
        
        # 构建交易
        nonce = web3.eth.get_transaction_count(agent_address)
        
        transaction = contract.functions.mintToken(
            Web3.to_checksum_address(agent_address),
            token_uri
        ).build_transaction({
            'chainId': 11155111,  # Ethereum Sepolia 测试网
            'gas': 300000,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce,
        })
        
        # 签名交易
        signed_txn = web3.eth.account.sign_transaction(transaction, AGENT_PRIVATE_KEY)
        
        # 发送交易
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_hash_hex = tx_hash.hex()
        
        # 等待确认
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        result = {
            "success": tx_receipt['status'] == 1,
            "tx_hash": tx_hash_hex,
            "gas_used": tx_receipt['gasUsed'],
            "block_number": tx_receipt['blockNumber'],
            "explorer_url": f"https://sepolia.etherscan.io/tx/{tx_hash_hex}",  # Ethereum Sepolia 浏览器
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"铸造失败: {str(e)}"}), 500


@app.route('/api/contract-config')
def contract_config():
    """获取合约配置"""
    try:
        # 读取合约 ABI
        abi_path = os.path.join(os.path.dirname(__file__), '..', 'contracts', 'MemoryToken_ABI.json')
        
        if os.path.exists(abi_path):
            with open(abi_path, 'r') as f:
                contract_abi = json.load(f)
        else:
            # 返回最小 ABI
            contract_abi = [
                {
                    "inputs": [{"internalType": "string", "name": "tokenURI", "type": "string"}],
                    "name": "mint",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "payable",
                    "type": "function"
                }
            ]
        
        return jsonify({
            "address": CONTRACT_ADDRESS,
            "abi": contract_abi,
            "chain_id": 11155111,  # Sepolia
            "chain_name": "Ethereum Sepolia"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/examples')
def examples():
    """获取示例故事"""
    example_stories = [
        {
            "title": "制陶师傅的最后一件作品",
            "content": """在一个古老的村庄里，住着一位年迈的制陶师傅。他用一生的时间，将泥土塑造成器皿，也将记忆烧制进每一件作品。他的双手布满裂纹，如同他捏制的陶罐表面的纹理。村里的年轻人都去了城市，只有他还守着这门即将失传的手艺。

一个雨夜，他最后一次点燃了窑火。火光中，他看到了自己的一生——童年时第一次触摸陶土的惊喜，青年时学艺的艰辛，以及晚年独自守望的孤独。当第二天村民们发现他时，窑里的陶罐已经烧制完成，温润如玉。而老人静静地坐在那里，脸上带着满足的笑容，仿佛他自己也成为了他最后的作品。

这个故事传遍了整个地区，那件最后的陶罐被送进了博物馆。人们说，如果你仔细聆听，还能听到陶罐里传来窑火燃烧的声音，那是一位匠人对时光最温柔的诉说。"""
        },
        {
            "title": "图书馆的守夜人",
            "content": """在城市的老城区，有一座百年历史的图书馆。每天闭馆后，守夜人老张会在书架间巡视。他说，这些书也需要有人陪伴。

有一次，他发现一本泛黄的日记本夹在两本厚重的历史书之间。日记的主人是一位在战争年代保护图书的年轻馆员，她冒着生命危险将珍贵的古籍转移到安全地带。日记最后一页写着："知识是人类最宝贵的财富，值得我们用生命去守护。"

老张将这本日记放在了图书馆最显眼的位置。从那以后，每个来访者都能读到这个故事。人们开始明白，守护知识不仅仅是一份工作，更是一种传承。"""
        },
        {
            "title": "奶奶的菜谱",
            "content": """奶奶去世后，我在她的旧箱子里发现了一本手写的菜谱。每一页都记录着一道菜的做法，还有她亲手画的小图。但最让我感动的，是每道菜后面都有一段话。

"红烧肉——你爷爷最爱吃，每次做这道菜他都会多吃一碗饭。"
"糖醋排骨——你爸小时候不爱吃饭，我就做这个哄他。"
"西红柿鸡蛋——你出生那天，我特意做了这道菜庆祝。"

原来每一道菜都承载着一个故事，一段回忆。我决定学会这些菜，不仅因为它们美味，更因为这是奶奶留给我的爱的密码。"""
        }
    ]
    
    return jsonify(example_stories)


# ============== 启动应用 ==============

if __name__ == '__main__':
    port = 5001  # 使用 5001 端口避免冲突
    print("\n" + "=" * 60)
    print("🌐 Digital Archivist Agent - Web 界面")
    print("=" * 60)
    print(f"\n✅ 应用启动成功！")
    print(f"\n📱 访问地址: http://localhost:{port}")
    print(f"🤖 AI 模型: {AI_MODEL}")
    print(f"🔗 AI 服务: 硅基流动 (SiliconFlow)")
    print(f"⛓️  区块链: Ethereum Sepolia (Alchemy)")
    print(f"📊 评分阈值: {SCORE_THRESHOLD}")
    print(f"📝 合约地址: {CONTRACT_ADDRESS[:10]}...{CONTRACT_ADDRESS[-4:]}")
    print(f"\n按 Ctrl+C 停止服务器\n")
    
    app.run(debug=True, host='0.0.0.0', port=port)


