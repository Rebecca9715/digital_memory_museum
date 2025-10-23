"""
Digital Memory Museum (DMM) | 数字记忆博物馆 - Web 界面
基于 Flask 的简单 Web 应用
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import requests
from datetime import datetime

from dotenv import load_dotenv
from web3 import Web3
from openai import OpenAI

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

# 启用 CORS - 用 try-catch 防止导入失败
try:
    CORS(app)
    print("✅ CORS 已启用")
except Exception as e:
    print(f"⚠️  CORS 导入失败: {e}，继续运行...")
    # 手动添加 CORS 头
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response

# ============== 配置 ==============

# Alchemy API 配置
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY", "")
if not ALCHEMY_API_KEY:
    print("⚠️  警告: ALCHEMY_API_KEY 环境变量未设置")
SEPOLIA_RPC = f"https://eth-sepolia.g.alchemy.com/v2/{ALCHEMY_API_KEY}" if ALCHEMY_API_KEY else "https://eth-sepolia.g.alchemy.com/v2/"

# 区块链配置
AGENT_PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0x0000000000000000000000000000000000000000")

# AI 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    print("⚠️  警告: OPENAI_API_KEY 环境变量未设置")
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
# 使用 try-catch 防止初始化失败导致应用崩溃
try:
    web3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC))
    print(f"✅ Web3 初始化成功，连接到: {SEPOLIA_RPC[:50]}...")
except Exception as e:
    print(f"⚠️  Web3 初始化警告: {e}")
    # 创建一个不连接的 Web3 实例作为降级方案
    web3 = Web3()

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
                    status_data["wallet_error"] = "Invalid private key configuration"
        
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
            return jsonify({"error": "Story content cannot be empty"}), 400
        
        if len(story_text) < 50:
            return jsonify({"error": "Story is too short, minimum 50 characters required"}), 400
        
        # AI 评估 - 使用硅基流动 API
        client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE
        )
        
        prompt = f"""You are a professional literary critic and cultural archivist. Please evaluate the value of the following humanistic story and return the assessment in JSON format.

Scoring Criteria (0-100):
- Emotional depth and authenticity (30 points)
- Cultural and historical value (25 points)
- Narrative quality and structure (20 points)
- Originality and uniqueness (15 points)
- Social significance and impact (10 points)

Story Content:
{story_text}

Please return in strict JSON format (without any markdown formatting):
{{
    "score": [integer from 0-100],
    "metadata_title": "[Brief title, max 50 characters]",
    "metadata_description": "[Detailed description summarizing the core value and characteristics of the story, 100-200 characters]",
    "feedback": "[Detailed evaluation feedback explaining the scoring rationale]",
    "image_prompt": "[English image generation prompt describing the core scene, atmosphere and visual elements of the story, suitable for AI art generation, 50-100 characters]"
}}"""
        
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional literary critic. Always return valid JSON format."},
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
        return jsonify({"error": f"Failed to parse AI response: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Evaluation failed: {str(e)}"}), 500


@app.route('/api/mint', methods=['POST'])
def mint():
    """铸造 NFT"""
    try:
        data = request.json
        metadata = data.get('metadata', {})
        
        if not metadata.get('metadata_title') or not metadata.get('metadata_description'):
            return jsonify({"error": "Incomplete metadata"}), 400
        
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
        return jsonify({"error": f"Minting failed: {str(e)}"}), 500


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
            "title": "The Potter's Final Masterpiece",
            "content": """In an ancient village lived an elderly potter. He had spent a lifetime shaping clay into vessels, firing memories into each creation. His hands were covered with cracks, like the textures on the pottery he crafted. All the young people had left for the cities, leaving only him to guard this dying craft.

On a rainy night, he lit his kiln for the last time. In the firelight, he saw his entire life—the wonder of first touching clay as a child, the hardships of apprenticeship in his youth, and the solitude of his twilight years as a guardian. When villagers found him the next day, the pottery in the kiln had been perfectly fired, smooth as jade. The old man sat there quietly, a contented smile on his face, as if he himself had become his final masterpiece.

The story spread throughout the region, and that last piece of pottery was sent to a museum. People say if you listen carefully, you can still hear the sound of the kiln fire burning within the vessel—a craftsman's most gentle conversation with time."""
        },
        {
            "title": "The Library Night Watchman",
            "content": """In the old quarter of the city stood a century-old library. Each night after closing, the watchman, Old Zhang, would patrol among the bookshelves. He said these books also needed company.

One day, he discovered a yellowed diary tucked between two thick history books. The diary belonged to a young librarian who had protected books during wartime, risking her life to move precious ancient texts to safety. The last page read: "Knowledge is humanity's most precious treasure, worth protecting with our lives."

Old Zhang placed this diary in the library's most prominent position. From then on, every visitor could read this story. People began to understand that protecting knowledge is not just a job—it's a legacy to be passed down."""
        },
        {
            "title": "Grandmother's Recipe Book",
            "content": """After my grandmother passed away, I found a handwritten recipe book in her old trunk. Each page recorded a dish's preparation method, with small drawings she had sketched herself. But what moved me most were the notes written after each recipe.

"Braised pork—your grandfather's favorite. He'd always have an extra bowl of rice when I made this."
"Sweet and sour ribs—your father was a picky eater as a child, so I made this to coax him."
"Tomato and eggs—I made this specially to celebrate the day you were born."

Each dish carried a story, a memory. I decided to learn all these recipes, not just because they were delicious, but because they were grandmother's code of love, left for me to decipher."""
        }
    ]
    
    return jsonify(example_stories)


# ============== 启动应用 ==============

if __name__ == '__main__':
    port = 5001  # 使用 5001 端口避免冲突
    print("\n" + "=" * 60)
    print("🏛️  Digital Memory Museum (DMM) | 数字记忆博物馆")
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


