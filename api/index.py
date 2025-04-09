#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Vercel 部署入口文件
"""

import sys
import os
import traceback

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 确保上传目录存在
os.makedirs('static/uploads', exist_ok=True)

try:
    # 尝试导入主应用
    from app import app
    print("应用导入成功")
except ImportError as e:
    print(f"导入错误: {e}")
    traceback.print_exc()
    # 尝试创建一个简单的应用作为备选
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def error_page():
        return jsonify({
            "error": str(e),
            "message": "应用导入失败，请检查日志",
            "traceback": traceback.format_exc()
        })

# Vercel 入口点
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080))) 