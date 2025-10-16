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
    
    # Vercel 会自动调用这个 app
    # 不需要额外的 handler 函数
    
except Exception as e:
    print(f"❌ Flask 应用导入失败: {e}")
    import traceback
    traceback.print_exc()
    raise

