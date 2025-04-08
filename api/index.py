#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Vercel 部署入口文件
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入主应用
from app import app

# 确保上传目录存在
os.makedirs('static/uploads', exist_ok=True)

# Vercel 入口点
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080))) 