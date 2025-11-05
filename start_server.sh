#!/bin/bash
# 启动订单系统服务端

echo "启动订单系统服务端..."
echo ""

# 检查配置文件
if [ ! -f "config/database.ini" ]; then
    echo "错误: 配置文件 config/database.ini 不存在"
    echo "请先运行 ./setup.sh 或手动创建配置文件"
    exit 1
fi

# 检查 Python 依赖
if ! python3 -c "import flask" 2>/dev/null; then
    echo "错误: Flask 未安装"
    echo "请运行: pip3 install -r requirements.txt"
    exit 1
fi

if ! python3 -c "import mysql.connector" 2>/dev/null; then
    echo "错误: mysql-connector-python 未安装"
    echo "请运行: pip3 install -r requirements.txt"
    exit 1
fi

# 启动服务端
cd server
python3 order_server.py
