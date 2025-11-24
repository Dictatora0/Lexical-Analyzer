#!/bin/bash

# 项目清理脚本 - 删除所有无用的临时文件

echo "======================================"
echo "清理项目临时文件"
echo "======================================"
echo ""

# 清理 macOS 系统文件
echo "[1/4] 清理 macOS 系统文件..."
find . -name ".DS_Store" -type f -delete
find . -name "._*" -type f -delete
find . -name ".AppleDouble" -type d -delete
find . -name ".LSOverride" -type f -delete
echo "✓ macOS 系统文件已清理"

# 清理 Python 缓存
echo "[2/4] 清理 Python 缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -type f -delete
find . -name "*.pyo" -type f -delete
find . -name "*.py[cod]" -type f -delete
echo "✓ Python 缓存已清理"

# 清理临时文件
echo "[3/4] 清理临时文件..."
find . -name "*.tmp" -type f -delete
find . -name "*.bak" -type f -delete
find . -name "*~" -type f -delete
echo "✓ 临时文件已清理"

# 清理 IDE 文件
echo "[4/4] 清理 IDE 文件..."
find . -name "*.swp" -type f -delete
find . -name "*.swo" -type f -delete
echo "✓ IDE 临时文件已清理"

echo ""
echo "======================================"
echo "清理完成！"
echo "======================================"
