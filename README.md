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

### 方法一：批量测试（推荐）

```bash
# 运行所有测试用例
./run_tests.sh
```

### 方法二：单个文件测试

```bash
# 基本用法
python src/lexical_analyzer.py <源文件路径> [输出文件路径]

# 示例
python src/lexical_analyzer.py tests/test_correct.mini outputs/result.txt
```

## 使用方法

### 命令行参数

```bash
python src/lexical_analyzer.py <源文件路径> [输出文件路径]
```

- **源文件路径**（必需）：Mini 语言源代码文件，以 `#` 结束
- **输出文件路径**（可选）：Token 序列输出文件，默认为 `tokens_output.txt`

### 详细示例

```bash
# 分析正确的程序
python src/lexical_analyzer.py tests/test_correct.mini outputs/output_correct.txt

# 分析包含错误的程序
python src/lexical_analyzer.py tests/test_error.mini outputs/output_error.txt

# 分析包含注释的程序
python src/lexical_analyzer.py tests/test_comment.mini outputs/output_comment.txt

# 测试所有运算符
python src/lexical_analyzer.py tests/test_operators.mini outputs/output_operators.txt
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

### 1. test_correct.mini - 正确程序测试

包含所有基本语法元素的正确程序。

### 2. test_error.mini - 错误检测测试

包含非法字符（如 `@`, `$`）的错误程序，用于测试错误检测功能。

### 3. test_comment.mini - 注释处理测试

包含单行和多行注释的程序，测试注释跳过功能。

### 4. test_operators.mini - 运算符测试

测试所有运算符的识别，特别是双字符运算符。

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
│   └── lexical_analyzer.py   # 词法分析器主程序
├── tests/                    # 测试用例目录
│   ├── test_correct.mini     # 正确程序测试用例
│   ├── test_error.mini       # 错误检测测试用例
│   ├── test_comment.mini     # 注释处理测试用例
│   └── test_operators.mini   # 运算符测试用例
├── outputs/                  # 输出文件目录
│   ├── output_correct.txt    # 正确程序分析结果
│   ├── output_error.txt      # 错误程序分析结果
│   └── output_comment.txt    # 注释程序分析结果
├── docs/                     # 文档目录
│   └── 实验报告.md           # 完整实验报告
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
