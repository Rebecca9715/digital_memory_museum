"""
Vercel Serverless Function 入口点
这个文件将 Flask 应用适配为 Vercel 可以调用的格式
"""
import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入 Flask 应用
from web.app import app

# Vercel 会自动调用这个 app
# 不需要额外的 handler 函数

