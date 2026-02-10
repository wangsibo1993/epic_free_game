#!/bin/bash

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到 Python3，请先安装 Python3。"
    exit 1
fi

echo "正在准备环境..."

# 创建临时虚拟环境以避免污染全局环境
VENV_DIR="tools/venv_cookies"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# 安装必要的库
echo "正在安装依赖库 (browser-cookie3)..."
pip install browser-cookie3 lz4 pycryptodome --quiet

# 运行提取脚本
echo "开始提取 Cookie..."
python3 tools/extract_cookies.py

# 退出虚拟环境
deactivate

# 提示清理（可选）
# rm -rf "$VENV_DIR"
