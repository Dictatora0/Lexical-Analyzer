#!/bin/bash

# Mini 语言词法分析器 v2.0 - 测试运行脚本

echo "======================================"
echo "Mini 语言词法分析器 v2.0 - 批量测试"
echo "======================================"
echo ""

# 创建输出目录
mkdir -p outputs

echo "【v2.0 新功能测试】"
echo ""

# 测试1: 浮点数支持
echo "[1/4] 测试浮点数支持..."
python src/lexical_analyzer.py tests/test_float.mini outputs/output_float.txt
echo ""

# 测试2: 字符串支持
echo "[2/4] 测试字符串支持..."
python src/lexical_analyzer.py tests/test_string.mini outputs/output_string.txt
echo ""

# 测试3: 综合功能
echo "[3/4] 测试综合功能（单行注释、浮点数、字符串）..."
python src/lexical_analyzer.py tests/test_features.mini outputs/output_features.txt
echo ""

# 测试4: 错误恢复机制
echo "[4/4] 测试错误恢复机制..."
python src/lexical_analyzer.py tests/test_errors.mini outputs/output_errors.txt 2>&1 | head -60
echo ""

echo "======================================"
echo "v2.0 测试完成！"
echo "======================================"
echo ""
echo "新增功能："
echo "  ✅ 浮点数支持"
echo "  ✅ 字符串常量（支持转义字符）"
echo "  ✅ 单行注释 //"
echo "  ✅ 符号表/常数表哈希优化 (O(1))"
echo "  ✅ 分派表消除 IF-ELSE 链"
echo "  ✅ 标准 EOF 处理"
echo "  ✅ 错误恢复机制（最多10个错误）"
echo ""
echo "结果已保存到 outputs/ 目录"
echo "详细改进说明见: docs/改进说明_v2.md"
echo "======================================"
