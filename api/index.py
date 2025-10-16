"""
Vercel Serverless Function 入口点
这个文件将 Flask 应用适配为 Vercel 可以调用的格式
"""
import sys
import os
import traceback as tb

# 将项目根目录添加到 Python 路径（必须在导入之前）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 尝试导入 Flask 应用
try:
    from web.app import app as flask_app
    app = flask_app
    
except Exception as e:
    # 如果导入失败，创建一个错误页面应用
    from flask import Flask
    app = Flask(__name__)
    
    # 捕获错误信息（在 except 块中）
    _error_message = str(e)
    _error_type = type(e).__name__
    _error_traceback = tb.format_exc()
    
    # 创建错误处理函数
    def make_error_handler(error_msg, error_tp, error_tb):
        def error_handler(path=''):
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>应用启动失败</title>
                <style>
                    body {{ 
                        font-family: monospace; 
                        margin: 40px; 
                        background-color: #f5f5f5; 
                    }}
                    .error-box {{ 
                        background-color: white; 
                        border-left: 4px solid #d32f2f; 
                        padding: 20px; 
                        margin: 20px 0; 
                    }}
                    h1 {{ color: #d32f2f; }}
                    pre {{ 
                        background-color: #f5f5f5; 
                        padding: 15px; 
                        overflow-x: auto; 
                        border: 1px solid #ddd;
                    }}
                </style>
            </head>
            <body>
                <h1>❌ Flask 应用启动失败</h1>
                
                <div class="error-box">
                    <h2>错误类型</h2>
                    <p><strong>{error_tp}</strong></p>
                </div>
                
                <div class="error-box">
                    <h2>错误信息</h2>
                    <p>{error_msg}</p>
                </div>
                
                <div class="error-box">
                    <h2>完整堆栈跟踪</h2>
                    <pre>{error_tb}</pre>
                </div>
                
                <div class="error-box">
                    <h2>系统信息</h2>
                    <p><strong>Python 版本:</strong> {sys.version}</p>
                    <p><strong>工作目录:</strong> {os.getcwd()}</p>
                    <p><strong>项目根目录:</strong> {project_root}</p>
                    <p><strong>Python 路径:</strong></p>
                    <pre>{chr(10).join(sys.path[:5])}</pre>
                </div>
                
                <div class="error-box">
                    <h2>环境变量状态</h2>
                    <p><strong>OPENAI_API_KEY:</strong> {'✅ 已设置' if os.getenv('OPENAI_API_KEY') else '❌ 未设置'}</p>
                    <p><strong>ALCHEMY_API_KEY:</strong> {'✅ 已设置' if os.getenv('ALCHEMY_API_KEY') else '❌ 未设置'}</p>
                    <p><strong>CONTRACT_ADDRESS:</strong> {os.getenv('CONTRACT_ADDRESS', '❌ 未设置')}</p>
                </div>
            </body>
            </html>
            """, 500
        return error_handler
    
    # 注册路由
    handler = make_error_handler(_error_message, _error_type, _error_traceback)
    app.route('/')(handler)
    app.route('/<path:path>')(handler)

