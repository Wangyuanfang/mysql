#!/bin/bash
# 订单系统安装脚本

echo "================================"
echo "订单管理系统 - 安装脚本"
echo "================================"
echo ""

# 检查 Python
echo "检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3"
    echo "请先安装 Python 3.7 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ 找到 Python $PYTHON_VERSION"
echo ""

# 检查 MySQL
echo "检查 MySQL..."
if ! command -v mysql &> /dev/null; then
    echo "警告: 未找到 MySQL 命令"
    echo "请确保已安装 MySQL 或 MariaDB"
else
    MYSQL_VERSION=$(mysql --version)
    echo "✓ 找到 $MYSQL_VERSION"
fi
echo ""

# 安装 Python 依赖
echo "安装 Python 依赖..."
pip3 install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Python 依赖安装成功"
else
    echo "✗ Python 依赖安装失败"
    exit 1
fi
echo ""

# 创建配置文件
echo "创建配置文件..."

if [ ! -f "config/database.ini" ]; then
    cp config/database.ini.example config/database.ini
    echo "✓ 已创建 config/database.ini"
    echo "  请编辑此文件，填入你的数据库连接信息"
else
    echo "! config/database.ini 已存在，跳过"
fi

if [ ! -f "config/client.ini" ]; then
    cp config/client.ini.example config/client.ini
    echo "✓ 已创建 config/client.ini"
else
    echo "! config/client.ini 已存在，跳过"
fi
echo ""

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p downloads
echo "✓ 已创建 downloads 目录"
echo ""

# 数据库初始化
echo "数据库初始化"
echo "--------------------------------"
echo "是否现在初始化数据库？(y/n)"
read -r answer

if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    echo ""
    echo "请输入 MySQL root 密码:"
    mysql -u root -p < database/schema.sql
    if [ $? -eq 0 ]; then
        echo "✓ 数据库初始化成功"
    else
        echo "✗ 数据库初始化失败"
        echo "你可以稍后手动执行: mysql -u root -p < database/schema.sql"
    fi
else
    echo "跳过数据库初始化"
    echo "你可以稍后手动执行: mysql -u root -p < database/schema.sql"
fi
echo ""

echo "================================"
echo "安装完成！"
echo "================================"
echo ""
echo "下一步操作："
echo "1. 编辑 config/database.ini 配置数据库连接"
echo "2. 如果跳过了数据库初始化，请手动执行："
echo "   mysql -u root -p < database/schema.sql"
echo "3. 启动服务端："
echo "   cd server && python3 order_server.py"
echo "4. 在另一个终端使用客户端："
echo "   python3 client/order_client.py --help"
echo ""
echo "详细使用说明请查看 ORDER_SYSTEM_README.md"
echo ""
