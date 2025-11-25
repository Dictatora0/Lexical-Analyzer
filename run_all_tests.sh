#!/bin/bash

# 综合测试运行脚本 - 支持参数选择

PYTHON="python3"
ANALYZER="src/lexical_analyzer.py"
OUTPUT_DIR="outputs"

# 确保输出目录存在
mkdir -p $OUTPUT_DIR

# 打印帮助信息
function print_help {
    echo "用法: ./run_all_tests.sh [选项]"
    echo "选项:"
    echo "  --all       运行所有测试（默认）"
    echo "  --basic     只运行基础功能测试"
    echo "  --v2        只运行 v2.0 新功能测试"
    echo "  --v3        只运行 v3.0 新功能测试"
    echo "  --error     只运行错误处理测试"
    echo "  --boundary  只运行边界条件测试"
    echo "  --stress    只运行压力测试"
    echo "  --help      显示此帮助信息"
}

# 运行单个测试文件
function run_test {
    local test_file=$1
    local output_file=$2
    local description=$3
    
    echo "正在运行: $description"
    echo "  文件: $test_file"
    $PYTHON $ANALYZER "$test_file" "$OUTPUT_DIR/$output_file"
    
    if [ $? -eq 0 ]; then
        echo "  ✅ 测试通过"
    else
        echo "  ❌ 测试失败"
    fi
    echo ""
}

# 基础功能测试
function run_basic_tests {
    echo "=== 基础功能测试 ==="
    # 假设已有基础测试文件，这里使用示例
    # run_test "tests/test_basic.mini" "output_basic.txt" "基础语法测试"
}

# v2.0 功能测试
function run_v2_tests {
    echo "=== v2.0 功能测试 ==="
    run_test "tests/test_features.mini" "output_v2_features.txt" "v2.0 综合特性"
    run_test "tests/test_float.mini" "output_v2_float.txt" "浮点数测试"
    run_test "tests/test_string.mini" "output_v2_string.txt" "字符串测试"
}

# v3.0 功能测试
function run_v3_tests {
    echo "=== v3.0 功能测试 ==="
    run_test "tests/test_v3_scientific.mini" "output_v3_scientific.txt" "科学计数法"
    run_test "tests/test_v3_operators.mini" "output_v3_operators.txt" "逻辑运算符"
    run_test "tests/test_v3_comprehensive.mini" "output_v3_comprehensive.txt" "v3.0 综合测试"
}

# 错误处理测试
function run_error_tests {
    echo "=== 错误处理测试 ==="
    run_test "tests/test_error_illegal_char.mini" "output_err_char.txt" "非法字符"
    run_test "tests/test_error_unclosed_string.mini" "output_err_string.txt" "未闭合字符串"
    run_test "tests/test_error_scientific.mini" "output_err_scientific.txt" "科学计数法错误"
    run_test "tests/test_error_illegal_op.mini" "output_err_op.txt" "非法运算符"
    run_test "tests/test_errors.mini" "output_err_general.txt" "一般错误测试"
}

# 边界条件测试
function run_boundary_tests {
    echo "=== 边界条件测试 ==="
    run_test "tests/test_boundary_numbers.mini" "output_boundary_num.txt" "数值边界"
    run_test "tests/test_boundary_strings.mini" "output_boundary_str.txt" "字符串边界"
}

# 压力测试
function run_stress_tests {
    echo "=== 压力测试 ==="
    run_test "tests/test_stress_nesting.mini" "output_stress_nesting.txt" "深度嵌套测试"
}

# 参数解析
if [ $# -eq 0 ]; then
    ARG="--all"
else
    ARG=$1
fi

echo "Mini 语言词法分析器 - 自动化测试套件"
echo "======================================"
echo ""

case $ARG in
    --all)
        run_v2_tests
        run_v3_tests
        run_error_tests
        run_boundary_tests
        run_stress_tests
        ;;
    --basic)
        run_basic_tests
        ;;
    --v2)
        run_v2_tests
        ;;
    --v3)
        run_v3_tests
        ;;
    --error)
        run_error_tests
        ;;
    --boundary)
        run_boundary_tests
        ;;
    --stress)
        run_stress_tests
        ;;
    --help)
        print_help
        ;;
    *)
        echo "未知选项: $ARG"
        print_help
        exit 1
        ;;
esac

echo "======================================"
echo "测试完成！结果保存在 $OUTPUT_DIR 目录"
