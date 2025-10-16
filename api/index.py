"""
Vercel Serverless Function 入口点
这个文件将 Flask 应用适配为 Vercel 可以调用的格式
"""
import sys
import os

# 打印启动信息（会显示在 Vercel 日志中）
print("🚀 Vercel Serverless Function 启动中...")
print(f"📂 Python 路径: {sys.path[:3]}")

# 将项目根目录添加到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
print(f"✅ 项目根目录: {project_root}")

try:
    # 导入 Flask 应用
    from web.app import app
    print("✅ Flask 应用导入成功")
    
    # 确保 app 作为模块的默认导出
    # Vercel 会寻找名为 'app' 的变量
    handler = app
    
except Exception as e:
    print(f"❌ Flask 应用导入失败: {e}")
    import traceback
    traceback.print_exc()
    
    # 创建一个简单的错误应用
    from flask import Flask
    handler = Flask(__name__)
    
    @handler.route('/')
    def error_handler():
        return f"❌ 应用启动失败: {str(e)}", 500

