# Mini 语言词法分析器

## 项目简介

本项目实现了一个完整的 Mini 语言词法分析器，能够将 Mini 语言源代码转换为 Token 序列，并生成符号表和常数表。

## Mini 语言定义

### 关键字

- `if`, `else`, `while`, `int`, `return`

### 运算符

- 算术运算符: `+`, `-`, `*`, `/`
- 关系运算符: `==`, `!=`, `<`, `<=`, `>`, `>=`
- 赋值运算符: `=`

### 界限符

- `(`, `)`, `{`, `}`, `;`, `,`

### 标识符

- 以字母或下划线开头，后跟字母、数字或下划线

### 常量

- 整数常量（如 `123`, `456`）

### 注释

- 块注释: `/* ... */`

### 结束符

- `#`

## 功能特性

1. **词法分析**: 将源代码分解为 Token 序列
2. **符号表管理**: 自动维护标识符符号表
3. **常数表管理**: 自动维护常数表
4. **注释处理**: 自动跳过块注释
5. **错误检测**: 检测并报告词法错误
6. **位置跟踪**: 记录每个 Token 的行号和列号
7. **文件输出**: 将分析结果保存到文件

## 快速开始

### 快速运行

```bash
# 运行完整测试套件
./run_all_tests.sh

# 单个文件测试
python src/lexical_analyzer.py tests/test_v3_scientific.mini outputs/result.txt
```

### 主要功能

**v3.0 新功能**：

- 🚀 **科学计数法**：支持 `1.2e-5`, `3.0E+10` 等格式
- 🎯 **逻辑运算符**：`&&` (AND), `||` (OR)
- ➕ **自增自减**：`++`, `--`
- 🏗️ **生成器模式**：内存高效，支持大文件
- 📏 **精确 Tab 处理**：列号与编辑器一致

**v2.0 功能**：

- ✅ 浮点数支持
- ✅ 字符串常量（支持转义字符）
- ✅ 单行注释 `//` 和块注释 `/* */`
- ✅ 符号表/常数表哈希优化 (O(1))
- ✅ 分派表模式，代码简洁
- ✅ 标准 EOF 处理
- ✅ 错误恢复机制（最多 10 个错误）

## 使用方法

### 命令行参数

```bash
python src/lexical_analyzer.py <源文件路径> [输出文件路径]
```

- **源文件路径**（必需）：Mini 语言源代码文件，以 `#` 结束
- **输出文件路径**（可选）：Token 序列输出文件，默认为 `tokens_output.txt`

### 详细示例

```bash
# 测试浮点数支持
python src/lexical_analyzer.py tests/test_float.mini outputs/output_float.txt

# 测试字符串支持
python src/lexical_analyzer.py tests/test_string.mini outputs/output_string.txt

# 测试综合功能
python src/lexical_analyzer.py tests/test_features.mini outputs/output_features.txt

# 测试错误恢复
python src/lexical_analyzer.py tests/test_errors.mini outputs/output_errors.txt
```

## 项目维护

### 清理临时文件

项目已配置 `.gitignore` 文件，自动忽略所有临时文件。如需手动清理，可运行：

```bash
# 清理所有临时文件（.DS_Store、__pycache__、*.pyc 等）
./clean.sh
```

清理内容包括：

- macOS 系统文件：`.DS_Store`、`._*`、`.AppleDouble` 等
- Python 缓存：`__pycache__/`、`*.pyc`、`*.pyo` 等
- 临时文件：`*.tmp`、`*.bak`、`*~` 等
- IDE 临时文件：`*.swp`、`*.swo` 等

## 测试用例

### 1. test_v3_scientific.mini - 科学计数法测试 (v3.0)

测试科学计数法的识别，如 `1.2e-5`、`3.0E+10`、`6.022e23`。

### 2. test_v3_operators.mini - 新运算符测试 (v3.0)

测试逻辑运算符 (`&&`, `||`) 和自增自减运算符 (`++`, `--`)。

### 3. test_v3_comprehensive.mini - v3.0 综合测试

测试 v3.0 所有新功能的组合使用，包括科学计数法、复杂运算符和 Tab 处理。

### 4. test_float.mini - 浮点数测试 (v2.0)

测试浮点数常量的识别，如 `3.14159`、`0.001`、`999.999`。

### 5. test_string.mini - 字符串测试 (v2.0)

测试字符串常量和转义字符，如 `"Hello\n"`、`"C:\\path"`。

### 6. test_features.mini - 综合功能测试 (v2.0)

测试 v2.0 的功能：浮点数、字符串、单行注释、块注释。

### 7. test_errors.mini - 错误恢复测试

测试错误检测和恢复机制，包含多个非法字符。

## 输出格式

### Token 格式

```
<类别码, '词素', Line:行号, Col:列号, Index:索引>
```

### 符号表格式

```
[索引] 标识符名称
```

### 常数表格式

```
[索引] 常数值
```

## 类别码定义

| 类别码 | Token 类型    | 说明          |
| ------ | ------------- | ------------- |
| 1      | IF            | 关键字 if     |
| 2      | ELSE          | 关键字 else   |
| 3      | WHILE         | 关键字 while  |
| 4      | INT           | 关键字 int    |
| 5      | RETURN        | 关键字 return |
| 6      | PLUS          | 运算符 +      |
| 7      | MINUS         | 运算符 -      |
| 8      | MULTIPLY      | 运算符 \*     |
| 9      | DIVIDE        | 运算符 /      |
| 10     | ASSIGN        | 运算符 =      |
| 11     | EQUAL         | 运算符 ==     |
| 12     | NOT_EQUAL     | 运算符 !=     |
| 13     | LESS          | 运算符 <      |
| 14     | LESS_EQUAL    | 运算符 <=     |
| 15     | GREATER       | 运算符 >      |
| 16     | GREATER_EQUAL | 运算符 >=     |
| 17     | LEFT_PAREN    | 界限符 (      |
| 18     | RIGHT_PAREN   | 界限符 )      |
| 19     | LEFT_BRACE    | 界限符 {      |
| 20     | RIGHT_BRACE   | 界限符 }      |
| 21     | SEMICOLON     | 界限符 ;      |
| 22     | COMMA         | 界限符 ,      |
| 23     | IDENTIFIER    | 标识符        |
| 24     | INTEGER       | 整数常量      |
| 25     | END           | 结束符 #      |

## 项目结构

```
Lexical-Analyzer/
├── src/                      # 源代码目录
│   └── lexical_analyzer.py   # 词法分析器（v3.0，~520行）
├── tests/                    # 测试用例目录
│   ├── test_v3_scientific.mini    # 科学计数法测试 (v3.0)
│   ├── test_v3_operators.mini     # 新运算符测试 (v3.0)
│   ├── test_v3_comprehensive.mini # 综合测试 (v3.0)
│   ├── test_float.mini       # 浮点数测试
│   ├── test_string.mini      # 字符串测试
│   ├── test_features.mini    # v2.0 综合功能测试
│   ├── test_errors.mini      # 错误恢复测试
│   └── (其他边界与压力测试文件)
├── outputs/                  # 输出结果目录
│   └── (自动生成的分析结果)
├── docs/                     # 文档目录
│   ├── 实验报告.md           # 完整实验报告
│   ├── 改进说明_v3.md        # v3.0 改进说明
│   ├── 改进说明_v2.md        # v2.0 改进说明
│   ├── v3.0_升级指南.md      # 升级指南
│   ├── v3.0_完成报告.md      # 项目完成报告
│   └── 项目概览.md           # 项目结构说明
├── run_all_tests.sh          # 自动化测试脚本（支持多种测试选项）
├── clean.sh                  # 清理脚本
└── README.md                 # 项目说明文档
```

## 技术实现

### 核心算法

- 基于有限自动机（DFA）的词法分析
- 最长匹配原则
- 前瞻一个字符的预读机制

### 数据结构

- **Token**: 存储类别码、词素、位置信息
- **SymbolTable**: 标识符符号表
- **ConstantTable**: 常数表
- **Keywords**: 关键字哈希表

### 错误处理

- 非法字符检测
- 未闭合注释检测
- 非法运算符组合检测
- 详细的错误位置信息

## 开发环境

- Python 3.6+
- 无第三方依赖

## 作者

词法分析器实习项目

## 许可证

MIT License
