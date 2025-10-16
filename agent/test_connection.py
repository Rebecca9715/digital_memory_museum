"""
测试脚本：验证环境配置是否正确
"""

import os
from dotenv import load_dotenv
from web3 import Web3

# 加载环境变量
load_dotenv()

def test_web3_connection():
    """测试 Web3 连接"""
    print("\n🧪 测试 1: Web3 连接")
    print("-" * 50)
    
    rpc_url = os.getenv("BASE_SEPOLIA_RPC", "https://sepolia.base.org")
    print(f"RPC URL: {rpc_url}")
    
    try:
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        is_connected = web3.is_connected()
        
        if is_connected:
            print("✅ Web3 连接成功!")
            
            # 获取链信息
            chain_id = web3.eth.chain_id
            block_number = web3.eth.block_number
            
            print(f"   Chain ID: {chain_id}")
            print(f"   当前区块高度: {block_number}")
            
            if chain_id == 84532:
                print("   ✅ 确认连接到 Base Sepolia 测试网")
            else:
                print(f"   ⚠️  警告: Chain ID {chain_id} 不是 Base Sepolia (84532)")
            
            return True
        else:
            print("❌ Web3 连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 连接错误: {str(e)}")
        return False


def test_wallet():
    """测试钱包私钥"""
    print("\n🧪 测试 2: 钱包配置")
    print("-" * 50)
    
    private_key = os.getenv("PRIVATE_KEY")
    
    if not private_key or private_key == "your_private_key_here":
        print("❌ 私钥未配置")
        print("   请在 .env 文件中设置 PRIVATE_KEY")
        return False
    
    try:
        web3 = Web3(Web3.HTTPProvider(os.getenv("BASE_SEPOLIA_RPC", "https://sepolia.base.org")))
        account = web3.eth.account.from_key(private_key)
        address = account.address
        
        print(f"✅ 钱包地址: {address}")
        
        # 检查余额
        balance = web3.eth.get_balance(address)
        balance_eth = web3.from_wei(balance, 'ether')
        
        print(f"   余额: {balance_eth:.6f} ETH")
        
        if balance_eth < 0.001:
            print("   ⚠️  警告: 余额较低，可能不足以支付 gas 费用")
            print("   💡 建议: 访问 Base Sepolia Faucet 获取测试 ETH")
        else:
            print("   ✅ 余额充足")
        
        return True
        
    except Exception as e:
        print(f"❌ 钱包配置错误: {str(e)}")
        return False


def test_contract():
    """测试合约配置"""
    print("\n🧪 测试 3: 合约配置")
    print("-" * 50)
    
    contract_address = os.getenv("CONTRACT_ADDRESS")
    
    if not contract_address or contract_address == "0x0000000000000000000000000000000000000000":
        print("⚠️  合约地址未配置")
        print("   请先部署合约，然后在 .env 文件中设置 CONTRACT_ADDRESS")
        return False
    
    try:
        web3 = Web3(Web3.HTTPProvider(os.getenv("BASE_SEPOLIA_RPC", "https://sepolia.base.org")))
        
        # 检查地址格式
        if not web3.is_address(contract_address):
            print(f"❌ 无效的合约地址: {contract_address}")
            return False
        
        checksum_address = web3.to_checksum_address(contract_address)
        print(f"✅ 合约地址: {checksum_address}")
        
        # 检查是否为合约
        code = web3.eth.get_code(checksum_address)
        
        if code == b'' or code == b'\x00':
            print("❌ 该地址不是合约")
            print("   请确认合约已正确部署")
            return False
        else:
            print("✅ 合约已部署")
            print(f"   字节码长度: {len(code)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ 合约配置错误: {str(e)}")
        return False


def test_openai():
    """测试 OpenAI API"""
    print("\n🧪 测试 4: OpenAI API")
    print("-" * 50)
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OpenAI API 密钥未配置")
        print("   请在 .env 文件中设置 OPENAI_API_KEY")
        return False
    
    try:
        from openai import OpenAI
        
        print(f"✅ API 密钥已配置 ({api_key[:10]}...)")
        
        # 简单测试 API 调用
        print("   正在测试 API 连接...")
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'test' if you can read this."}
            ],
            max_tokens=10
        )
        
        print("✅ OpenAI API 连接成功!")
        print(f"   响应: {response.choices[0].message.content.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API 错误: {str(e)}")
        print("   请检查:")
        print("   1. API 密钥是否正确")
        print("   2. 账户是否有余额/配额")
        print("   3. 网络连接是否正常")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("🔧 Digital Archivist Agent - 环境配置测试")
    print("=" * 60)
    
    # 检查 .env 文件是否存在
    if not os.path.exists('.env'):
        print("\n❌ 错误: .env 文件不存在")
        print("\n请执行以下步骤:")
        print("1. 复制 env.example 为 .env")
        print("   cp env.example .env")
        print("2. 编辑 .env 文件，填写必要的配置")
        return
    
    results = {
        "Web3 连接": test_web3_connection(),
        "钱包配置": test_wallet(),
        "合约配置": test_contract(),
        "OpenAI API": test_openai()
    }
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print("-" * 60)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！你已准备好运行 Agent！")
        print("\n下一步:")
        print("   python archivist_agent.py")
    else:
        print("\n⚠️  部分测试失败，请根据上述提示修复配置")
        print("\n如需帮助，请查看:")
        print("   - README.md")
        print("   - DEPLOYMENT_GUIDE.md")
        print("   - QUICKSTART.md")


if __name__ == "__main__":
    main()


