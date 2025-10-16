#!/bin/bash

# Digital Archivist Agent - Web 界面启动脚本

echo "=========================================="
echo "🤖 Digital Archivist Agent"
echo "   Web 界面启动脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 .env 文件
echo -e "${BLUE}📋 检查配置文件...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 文件不存在${NC}"
    echo ""
    echo "正在创建 .env 文件..."
    cp env.example .env
    echo -e "${GREEN}✓${NC} .env 文件已创建"
    echo ""
    echo -e "${RED}⚠️  重要：请编辑 .env 文件并填写以下信息：${NC}"
    echo "   1. PRIVATE_KEY         - 你的 MetaMask 私钥"
    echo "   2. OPENAI_API_KEY      - OpenAI API 密钥"
    echo "   3. CONTRACT_ADDRESS    - 部署后的合约地址"
    echo ""
    read -p "按 Enter 继续编辑配置文件，或按 Ctrl+C 取消..."
    
    # 尝试打开编辑器
    if command -v code &> /dev/null; then
        code .env
    elif command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    else
        echo "请手动编辑 .env 文件"
    fi
    
    echo ""
    read -p "配置完成后，按 Enter 继续..."
else
    echo -e "${GREEN}✓${NC} .env 文件存在"
fi

echo ""
echo -e "${BLUE}📦 检查 Python 依赖...${NC}"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗${NC} Python 3 未安装"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python $(python3 --version | awk '{print $2}')"

# 检查依赖
cd web
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}✗${NC} requirements.txt 不存在"
    exit 1
fi

echo ""
echo -e "${BLUE}📥 安装/更新依赖...${NC}"
pip3 install -r requirements.txt -q

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 依赖安装完成"
else
    echo -e "${RED}✗${NC} 依赖安装失败"
    exit 1
fi

# 检查端口占用
echo ""
echo -e "${BLUE}🔍 检查端口 5000...${NC}"
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  端口 5000 已被占用${NC}"
    read -p "是否终止占用进程并继续？[y/N]: " kill_process
    if [[ $kill_process == "y" || $kill_process == "Y" ]]; then
        lsof -ti:5000 | xargs kill -9
        echo -e "${GREEN}✓${NC} 已释放端口 5000"
    else
        echo "请手动释放端口 5000 后重试"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} 端口 5000 可用"
fi

# 启动服务器
echo ""
echo "=========================================="
echo -e "${GREEN}🚀 启动 Web 服务器...${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📱 访问地址:${NC} http://localhost:5000"
echo -e "${BLUE}🔗 或访问:${NC}  http://127.0.0.1:5000"
echo ""
echo -e "${YELLOW}💡 提示：${NC}"
echo "   - 按 Ctrl+C 停止服务器"
echo "   - 首次使用请先部署智能合约"
echo "   - 确保 .env 文件配置正确"
echo ""
echo "=========================================="
echo ""

# 启动 Flask 应用
python3 app.py

# 如果服务器停止
echo ""
echo "=========================================="
echo "👋 服务器已停止"
echo "=========================================="



