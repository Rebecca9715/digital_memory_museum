"""
Vercel Serverless Function 入口点
这个文件将 Flask 应用适配为 Vercel 可以调用的格式
"""
import sys
import os

# 打印启动信息（会显示在 Vercel 日志中）
print("=" * 60)
print("🚀 Vercel Serverless Function 启动中...")
print(f"📂 Python 版本: {sys.version}")
print(f"📂 Python 路径: {sys.path[:3]}")
print(f"📂 当前工作目录: {os.getcwd()}")
print(f"📂 环境变量 OPENAI_API_KEY: {'已设置' if os.getenv('OPENAI_API_KEY') else '未设置'}")
print(f"📂 环境变量 ALCHEMY_API_KEY: {'已设置' if os.getenv('ALCHEMY_API_KEY') else '未设置'}")
print(f"📂 环境变量 CONTRACT_ADDRESS: {os.getenv('CONTRACT_ADDRESS', '未设置')}")
print("=" * 60)

# 将项目根目录添加到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
print(f"✅ 项目根目录: {project_root}")

try:
    # 导入 Flask 应用
    print("📦 正在导入 Flask 应用...")
    from web.app import app
    print("✅ Flask 应用导入成功")
    print(f"✅ Flask 应用名称: {app.name}")
    print(f"✅ Flask 路由: {[str(rule) for rule in app.url_map.iter_rules()][:5]}")
    
    # Vercel 会寻找名为 'app' 的变量作为默认导出
    # 这是标准的 Vercel Python 函数格式
    
except Exception as e:
    print("=" * 60)
    print(f"❌ Flask 应用导入失败: {e}")
    print(f"❌ 错误类型: {type(e).__name__}")
    import traceback
    print("❌ 完整堆栈跟踪:")
    traceback.print_exc()
    print("=" * 60)
    
    # 创建一个简单的错误应用
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error_handler():
        return f"""
        <html>
        <head><title>应用启动失败</title></head>
        <body>
            <h1>❌ 应用启动失败</h1>
            <p><strong>错误信息：</strong> {str(e)}</p>
            <p><strong>错误类型：</strong> {type(e).__name__}</p>
            <p>请检查 Vercel Function Logs 获取详细信息</p>
        </body>
        </html>
        """, 500
    
    @app.route('/<path:path>')
    def catch_all(path):
        return error_handler()

