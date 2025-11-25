#!/bin/bash

# v3.0 测试脚本 - 测试新功能

echo "======================================"
echo "Mini 语言词法分析器 v3.0 测试"
echo "======================================"
echo ""

# 设置 Python 路径
PYTHON="python3"
ANALYZER="src/lexical_analyzer.py"

# 测试1：科学计数法
echo "[1/3] 测试科学计数法（Scientific Notation）..."
$PYTHON $ANALYZER tests/test_v3_scientific.mini outputs/output_v3_scientific.txt
echo ""

# 测试2：逻辑运算符和自增自减
echo "[2/3] 测试逻辑运算符（&&, ||）和自增自减（++, --）..."
$PYTHON $ANALYZER tests/test_v3_operators.mini outputs/output_v3_operators.txt
echo ""

# 测试3：综合测试
echo "[3/3] 测试 v3.0 综合功能..."
$PYTHON $ANALYZER tests/test_v3_comprehensive.mini outputs/output_v3_comprehensive.txt
echo ""

echo "======================================"
echo "v3.0 测试完成！"
echo "======================================"
echo ""
echo "新增功能："
echo "  ✅ 科学计数法 (1.2e-5, 3.0E+10)"
echo "  ✅ 逻辑运算符 (&&, ||)"
echo "  ✅ 自增自减运算符 (++, --)"
echo "  ✅ 生成器模式 (Lazy Evaluation)"
echo "  ✅ 精确的 Tab 列号处理"
echo ""
echo "结果已保存到 outputs/ 目录"
echo "详细改进说明见: docs/改进说明_v3.md"
echo "======================================"
