@echo off
REM Digital Archivist Agent - Web 界面启动脚本 (Windows)

echo ==========================================
echo 🤖 Digital Archivist Agent
echo    Web 界面启动脚本
echo ==========================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查 .env 文件
echo 📋 检查配置文件...
if not exist ".env" (
    echo ⚠️  .env 文件不存在
    echo.
    echo 正在创建 .env 文件...
    copy env.example .env
    echo ✓ .env 文件已创建
    echo.
    echo ⚠️  重要：请编辑 .env 文件并填写以下信息：
    echo    1. PRIVATE_KEY         - 你的 MetaMask 私钥
    echo    2. OPENAI_API_KEY      - OpenAI API 密钥
    echo    3. CONTRACT_ADDRESS    - 部署后的合约地址
    echo.
    pause
    notepad .env
    echo.
    pause
) else (
    echo ✓ .env 文件存在
)

echo.
echo 📦 检查 Python 依赖...

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python 未安装
    echo 请先安装 Python 3.8 或更高版本
    pause
    exit /b 1
)

echo ✓ Python 已安装

REM 安装依赖
echo.
echo 📥 安装/更新依赖...
cd web
pip install -r requirements.txt -q

if %errorlevel% neq 0 (
    echo ✗ 依赖安装失败
    pause
    exit /b 1
)

echo ✓ 依赖安装完成

REM 启动服务器
echo.
echo ==========================================
echo 🚀 启动 Web 服务器...
echo ==========================================
echo.
echo 📱 访问地址: http://localhost:5000
echo 🔗 或访问:  http://127.0.0.1:5000
echo.
echo 💡 提示：
echo    - 按 Ctrl+C 停止服务器
echo    - 首次使用请先部署智能合约
echo    - 确保 .env 文件配置正确
echo.
echo ==========================================
echo.

REM 启动 Flask 应用
python app.py

REM 如果服务器停止
echo.
echo ==========================================
echo 👋 服务器已停止
echo ==========================================
pause



