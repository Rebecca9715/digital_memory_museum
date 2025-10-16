#!/bin/bash

echo "🚀 准备部署到 Vercel..."
echo ""

# 检查是否已安装 Vercel CLI
if ! command -v vercel &> /dev/null
then
    echo "❌ Vercel CLI 未安装"
    echo "请运行: npm install -g vercel"
    echo "或访问 https://vercel.com 使用 GitHub 部署"
    exit 1
fi

echo "✅ Vercel CLI 已安装"
echo ""

# 检查是否是 Git 仓库
if [ ! -d .git ]; then
    echo "📦 初始化 Git 仓库..."
    git init
    git add .
    git commit -m "Initial commit: DAA MVP with NFT minting"
    echo "✅ Git 仓库已初始化"
else
    echo "✅ Git 仓库已存在"
fi

echo ""
echo "⚠️  重要提醒："
echo "   请确保 .env 文件中的敏感信息（如私钥）已被 .gitignore 忽略"
echo "   部署后需要在 Vercel 后台手动添加环境变量"
echo ""

read -p "是否继续部署到 Vercel? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ 部署已取消"
    exit 1
fi

echo ""
echo "🔐 开始 Vercel 部署..."
vercel

echo ""
echo "✅ 部署完成！"
echo ""
echo "📝 下一步:"
echo "   1. 访问 Vercel Dashboard: https://vercel.com/dashboard"
echo "   2. 找到您的项目并进入设置 (Settings)"
echo "   3. 在 Environment Variables 中添加以下变量:"
echo "      - OPENAI_API_KEY"
echo "      - OPENAI_API_BASE"
echo "      - AI_MODEL"
echo "      - BASE_SEPOLIA_RPC"
echo "      - ALCHEMY_API_KEY"
echo "      - CONTRACT_ADDRESS"
echo "   4. 重新部署: vercel --prod"
echo ""
echo "🎉 完成后访问您的应用 URL！"

