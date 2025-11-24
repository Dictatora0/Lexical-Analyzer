#!/bin/bash

# Mini 语言词法分析器 - 测试运行脚本

echo "======================================"
echo "Mini 语言词法分析器 - 批量测试"
echo "======================================"
echo ""

# 创建输出目录（如果不存在）
mkdir -p outputs

# 测试1: 正确程序
echo "[1/4] 测试正确程序..."
python src/lexical_analyzer.py tests/test_correct.mini outputs/output_correct.txt
echo ""

# 测试2: 错误检测
echo "[2/4] 测试错误检测..."
python src/lexical_analyzer.py tests/test_error.mini outputs/output_error.txt
echo ""

# 测试3: 注释处理
echo "[3/4] 测试注释处理..."
python src/lexical_analyzer.py tests/test_comment.mini outputs/output_comment.txt
echo ""

# 测试4: 运算符测试
echo "[4/4] 测试运算符..."
python src/lexical_analyzer.py tests/test_operators.mini outputs/output_operators.txt
echo ""

echo "======================================"
echo "所有测试完成！"
echo "结果已保存到 outputs/ 目录"
echo "======================================"
