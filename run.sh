#!/bin/bash

# 启动脚本

echo "🚀 Starting MiniClaw..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  虚拟环境不存在，正在创建..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "❌ .env 文件不存在！"
    echo "请先复制 .env.example 并配置："
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# 安装依赖
pip install -q -r requirements.txt

# 加载环境变量
export $(cat .env | grep -v '^#' | xargs)

# 启动 bot
python bot.py
