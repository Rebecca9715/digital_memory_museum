#!/bin/bash

# 更新合约地址脚本
# 使用方法: ./更新合约地址.sh 0x您的合约地址

if [ -z "$1" ]; then
    echo "❌ 错误：请提供合约地址"
    echo "使用方法: ./更新合约地址.sh 0x您的合约地址"
    exit 1
fi

CONTRACT_ADDRESS=$1

# 验证地址格式
if [[ ! $CONTRACT_ADDRESS =~ ^0x[a-fA-F0-9]{40}$ ]]; then
    echo "❌ 错误：无效的合约地址格式"
    echo "地址应该是 42 个字符，以 0x 开头"
    exit 1
fi

echo "🔧 正在更新合约地址..."
echo "新地址: $CONTRACT_ADDRESS"

# 备份原文件
cp /Users/rebeccawang/web3/dda/DAA_MVP/.env /Users/rebeccawang/web3/dda/DAA_MVP/.env.backup

# 更新合约地址
sed -i '' "s/CONTRACT_ADDRESS=.*/CONTRACT_ADDRESS=$CONTRACT_ADDRESS/" /Users/rebeccawang/web3/dda/DAA_MVP/.env

echo "✅ 合约地址已更新！"
echo "备份文件: .env.backup"
echo ""
echo "📝 当前配置："
grep CONTRACT_ADDRESS /Users/rebeccawang/web3/dda/DAA_MVP/.env
echo ""
echo "🔄 请重启服务器使配置生效"

