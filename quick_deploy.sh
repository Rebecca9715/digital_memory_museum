#!/bin/bash

echo "🚀 开始部署到 Vercel..."
echo ""

# 检查是否安装了 Vercel CLI
if ! command -v vercel &> /dev/null
then
    echo "📦 Vercel CLI 未安装，正在安装..."
    npm install -g vercel
    echo ""
fi

echo "🔐 请登录 Vercel（浏览器会自动打开）"
echo "如果已经登录，会跳过此步骤"
vercel login
echo ""

echo "📤 开始部署到生产环境..."
echo "这会从您的本地代码直接部署到 Vercel"
echo ""

cd "$(dirname "$0")"
vercel --prod

echo ""
echo "✅ 部署完成！"
echo "请访问 Vercel Dashboard 查看部署状态"
echo ""
echo "⚠️  不要忘记在 Vercel 配置环境变量！"
echo "详见 VERCEL_DEPLOY_GUIDE.md"

