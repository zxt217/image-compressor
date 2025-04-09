#!/bin/bash

# 输出环境信息
echo "当前Python版本:"
python --version

# 尝试安装系统依赖
if command -v apt-get &> /dev/null; then
    echo "Debian/Ubuntu环境, 尝试安装依赖..."
    apt-get update
    apt-get install -y --no-install-recommends libjpeg-dev zlib1g-dev
elif command -v yum &> /dev/null; then
    echo "RHEL/CentOS环境, 尝试安装依赖..."
    yum install -y libjpeg-devel zlib-devel
fi

# 安装Python依赖
echo "安装Python依赖..."
pip install -r requirements.txt

echo "构建完成!" 