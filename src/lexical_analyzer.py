#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Mini 语言词法分析器 v3.0 - 专业版

v2.0 改进内容：
1. 支持浮点数
2. 支持字符串常量
3. 支持单行注释 //
4. 符号表/常数表哈希优化
5. 使用分派表消除巨型 IF-ELSE
6. 标准 EOF 处理
7. 错误恢复机制

v3.0 新增改进：
1. 支持科学计数法 (1.2e-5, 3.0E+10)
2. 生成器模式 (Lazy Evaluation)
3. 逻辑运算符 (&&, ||) 和自增自减 (++, --)
4. 精确的 Tab 处理（列号计算）
"""

import sys
from typing import List, Optional, Dict, Union
from enum import IntEnum


class TokenType(IntEnum):
    """Mini 语言中所有 Token 类型的枚举。

    词法分析阶段只关心“这是一类什么东西”，
    比如：关键字、标识符、整数、浮点数、运算符、括号等，
    统一用枚举值来表达，便于后续语法分析和错误信息输出。
    """
    IF = 1
    ELSE = 2
    WHILE = 3
    INT = 4
    RETURN = 5
    PLUS = 6
    MINUS = 7
    MULTIPLY = 8
    DIVIDE = 9
    ASSIGN = 10
    EQUAL = 11
    NOT_EQUAL = 12
    LESS = 13
    LESS_EQUAL = 14
    GREATER = 15
    GREATER_EQUAL = 16
    LEFT_PAREN = 17
    RIGHT_PAREN = 18
    LEFT_BRACE = 19
    RIGHT_BRACE = 20
    SEMICOLON = 21
    COMMA = 22
    IDENTIFIER = 23
    INTEGER = 24
    FLOAT = 26
    STRING = 27
    EOF = 28

    # v3.0 新增
    AND = 29          # &&
    OR = 30           # ||
    INCREMENT = 31    # ++
    DECREMENT = 32    # --


class Token:
    """词法单元（Token）的数据结构。

    一个 Token 对应源代码中的一个最小“记号”，例如：
    - 关键字：if, while;
    - 标识符：变量名、函数名等；
    - 常量：数字字面量、字符串字面量；
    - 分隔符：括号、逗号、分号等。

    属性说明：
    - type:       TokenType 枚举值，表示记号的类别；
    - value:      源代码中的原始文本（例如 "if"、"abc"、"123"）；
    - line:       记号在源文件中的行号（从 1 开始）；
    - column:     记号在源文件中的列号（从 1 开始），尽量与编辑器显示一致；
    - attr_index: 若需要在符号表/常数表中查找附加信息，则记录对应索引，否则为 -1。
    """

    def __init__(self, token_type: int, value: str, line: int, column: int, attr_index: int = -1):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
        self.attr_index = attr_index
    
    def __repr__(self):
        if self.attr_index >= 0:
            return f"<{self.type}, '{self.value}', Line:{self.line}, Col:{self.column}, Index:{self.attr_index}>"
        else:
            return f"<{self.type}, '{self.value}', Line:{self.line}, Col:{self.column}>"


class SymbolEntry:
    """符号表中的一项。

    对于标识符（变量名、函数名等），词法分析阶段只负责“发现和登记”，
    不做语义检查。这里记录：
    - name: 标识符的名字；
    - index: 在符号表中的序号，供 Token.attr_index 使用。
    """

    def __init__(self, name: str, index: int):
        self.name = name
        self.index = index
    
    def __repr__(self):
        return f"[{self.index}] {self.name}"


class ConstantEntry:
    """常数表中的一项。

    对于整数、浮点数、字符串等字面量，为了避免重复存储，
    可以把它们集中放在常数表里，只在 Token 里保存一个索引。

    - value: 常量的实际值（已经转换成 int/float/str）；
    - index: 在常数表中的序号；
    - const_type: 常量类型字符串，例如 "int"、"float"、"string"。
    """

    def __init__(self, value: Union[int, float, str], index: int, const_type: str = "int"):
        self.value = value
        self.index = index
        self.const_type = const_type
    
    def __repr__(self):
        return f"[{self.index}] {self.value} ({self.const_type})"


class LexicalAnalyzer:
    """Mini 语言的词法分析器。
    
    职责：
    1. 顺序读取源代码字符流，切分出 Token 序列；
    2. 维护符号表（标识符）和常数表（字面量）；
    3. 在发现错误时尽量继续扫描，方便一次性看到更多问题。
    """
    MAX_ERRORS = 10
    
    def __init__(self, source_code: str):
        # 把整段源代码读入内存，准备进行顺序扫描
        # pos 表示当前字符在字符串中的下标
        # line/column 用来在报错时给出精确的行列位置
        # current_char 始终指向“当前正在看的字符”，避免频繁索引 self.source
        self.source = source_code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source[0] if source_code else None
        # Tab 宽度固定为 4，用于计算列号（和大部分编辑器的默认设置一致）
        self.tab_width = 4  # v3.0: Tab 宽度设置
        
        # 关键字表：扫描到对应单词时直接映射为关键字 Token
        self.keywords = {
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'int': TokenType.INT,
            'return': TokenType.RETURN
        }
        
        # v3.0: 双字符运算符映射表
        self.double_char_tokens = {
            '==': TokenType.EQUAL,
            '!=': TokenType.NOT_EQUAL,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL,
            '&&': TokenType.AND,
            '||': TokenType.OR,
            '++': TokenType.INCREMENT,
            '--': TokenType.DECREMENT
        }
        
        self.simple_tokens = {
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '*': TokenType.MULTIPLY,
        }
        
        self.symbol_table: List[SymbolEntry] = []
        self.symbol_map: Dict[str, int] = {}
        
        self.constant_table: List[ConstantEntry] = []
        self.constant_map: Dict[Union[int, float, str], int] = {}
        
        self.tokens: List[Token] = []
        self.errors: List[str] = []
    
    def error(self, message: str):
        # 统一的错误处理入口：
        # 1. 把错误信息记录到 errors 列表，方便在末尾集中输出；
        # 2. 立刻打印到终端，便于调试时第一时间看到问题；
        # 3. 不直接抛异常，而是尽量继续往后扫描，收集更多错误信息。
        error_msg = f"错误 (行 {self.line}, 列 {self.column}): {message}"
        self.errors.append(error_msg)
        print(error_msg)
        
        # 仅在错误数量第一次达到上限时给出提示，不中断后续分析
        if len(self.errors) == self.MAX_ERRORS:
            print(f"\n警告: 错误数量已达到 {self.MAX_ERRORS} 个，但继续分析...")
    
    def advance(self):
        """v3.0: 改进的 advance 方法，支持精确的 Tab 列号计算"""
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        elif self.current_char == '\t':
            # 计算下一个制表位 (Tab Stop)
            # 公式：当前列 + (宽度 - (当前列-1) % 宽度)
            self.column += (self.tab_width - (self.column - 1) % self.tab_width)
        else:
            self.column += 1
        
        self.pos += 1
        if self.pos < len(self.source):
            self.current_char = self.source[self.pos]
        else:
            self.current_char = None
    
    def peek(self, offset: int = 1) -> Optional[str]:
        peek_pos = self.pos + offset
        if peek_pos < len(self.source):
            return self.source[peek_pos]
        return None
    
    def skip_whitespace(self):
        # 连续吞掉空格、Tab、换行等空白字符
        # 注意：这里不会产生任何 Token，只是把指针移到下一个“有意义”的字符上
        while self.current_char and self.current_char in ' \t\n\r':
            self.advance()
    
    def skip_block_comment(self) -> bool:
        # 跳过块注释 /* ... */
        # 进入本函数时，当前字符是 '/'，需要再看一位确认是否为 '/*'
        if self.current_char == '/' and self.peek() == '*':
            # 先跳过起始符号 '/*'
            self.advance()
            self.advance()
            
            # 一直向前扫，直到遇到对应的 '*/' 或者文件结束
            while self.current_char:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()
                    self.advance()
                    return True
                self.advance()
            
            # 能走到这里说明文件结束前都没有遇到 '*/'
            self.error("未闭合的块注释")
            return False
        return False
    
    def skip_line_comment(self) -> bool:
        # 跳过 // 单行注释
        # 从当前的 // 一直跳到换行符为止（换行本身也一并吃掉）
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char and self.current_char != '\n':
                self.advance()
            if self.current_char == '\n':
                self.advance()
            return True
        return False
    
    def read_identifier(self) -> Token:
        # 读取以字母或下划线开头的一串字符：
        # 如果在关键字表中，则返回关键字 Token；
        # 否则当作普通标识符写入符号表，并返回对应索引。
        start_line = self.line
        start_column = self.column
        result = ''
        
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        if result in self.keywords:
            return Token(self.keywords[result], result, start_line, start_column)
        else:
            index = self.add_to_symbol_table(result)
            return Token(TokenType.IDENTIFIER, result, start_line, start_column, index)
    
    def read_number(self) -> Token:
        """v3.0: 支持科学计数法 (1.2e-5, 3.0E+10)"""
        # 整数、小数和科学计数法统一在这里处理
        # start_line/start_column 用来在出错时给出准确位置
        start_line = self.line
        start_column = self.column
        result = ''
        is_float = False
        
        # 读取整数部分和小数部分
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if is_float:
                    break
                if not self.peek() or not self.peek().isdigit():
                    break
                is_float = True
            result += self.current_char
            self.advance()
        
        # v3.0: 处理科学计数法指数部分 (e 或 E)，例如 1.23e-4 或 3E+8
        if self.current_char and self.current_char.lower() == 'e':
            result += self.current_char
            self.advance()
            
            # 处理指数符号 (+/-)
            if self.current_char and self.current_char in '+-':
                result += self.current_char
                self.advance()
            
            # 指数后面必须跟数字
            if not self.current_char or not self.current_char.isdigit():
                self.error("科学计数法格式错误: 指数后缺少数字")
                return Token(TokenType.FLOAT, result, start_line, start_column, -1)
            
            # 读取指数数字部分
            while self.current_char and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            
            is_float = True  # 只要有 'e'，一定是浮点数
        
        # 存入常数表：浮点和整数分别记录类型，后续可以根据类型做不同处理
        if is_float:
            try:
                value = float(result)
                index = self.add_to_constant_table(value, "float")
                return Token(TokenType.FLOAT, result, start_line, start_column, index)
            except ValueError:
                self.error(f"无效的浮点数格式: {result}")
                return Token(TokenType.FLOAT, result, start_line, start_column, -1)
        else:
            value = int(result)
            index = self.add_to_constant_table(value, "int")
            return Token(TokenType.INTEGER, result, start_line, start_column, index)
    
    def read_string(self) -> Token:
        # 读取字符串常量，支持部分转义序列
        start_line = self.line
        start_column = self.column
        quote_char = self.current_char
        self.advance()
        
        result = ''
        while self.current_char and self.current_char != quote_char:
            if self.current_char == '\n':
                # 遇到换行说明引号没有闭合
                self.error(f"字符串常量未闭合")
                break
            
            if self.current_char == '\\':
                self.advance()
                if self.current_char in 'ntr"\'\\':
                    # 常见转义字符映射
                    escape_map = {'n': '\n', 't': '\t', 'r': '\r', '"': '"', "'": "'", '\\': '\\'}
                    result += escape_map.get(self.current_char, self.current_char)
                    self.advance()
                else:
                    result += self.current_char
                    self.advance()
            else:
                result += self.current_char
                self.advance()
        
        if self.current_char == quote_char:
            self.advance()
        else:
            # 扫描结束仍未遇到结束引号
            self.error(f"字符串常量未闭合")
        
        index = self.add_to_constant_table(result, "string")
        return Token(TokenType.STRING, result, start_line, start_column, index)
    
    def add_to_symbol_table(self, name: str) -> int:
        # 符号表去重并返回索引
        # 这样语法分析阶段只需要保存整数索引，而不必反复存储完整标识符字符串
        if name in self.symbol_map:
            return self.symbol_map[name]
        
        index = len(self.symbol_table)
        self.symbol_table.append(SymbolEntry(name, index))
        self.symbol_map[name] = index
        return index
    
    def add_to_constant_table(self, value: Union[int, float, str], const_type: str) -> int:
        # 常数表去重并返回索引
        # 相同字面量（比如多处写的 0 或 1.0）只保留一份，节省空间
        if value in self.constant_map:
            return self.constant_map[value]
        
        index = len(self.constant_table)
        self.constant_table.append(ConstantEntry(value, index, const_type))
        self.constant_map[value] = index
        return index
    
    def get_next_token(self) -> Optional[Token]:
        # 主扫描循环，根据当前字符生成下一个记号：
        # 1. 先跳过空白和注释；
        # 2. 再根据首字符判断是标识符、数字、字符串还是运算符/分隔符；
        # 3. 每次调用最多前进到下一个 Token 边界，或者在遇到非法字符时尝试报错并恢复。
        while self.current_char:
            if self.current_char in ' \t\n\r':
                self.skip_whitespace()
                continue
            
            if self.current_char == '/' and self.peek() == '*':
                self.skip_block_comment()
                continue
            
            if self.current_char == '/' and self.peek() == '/':
                self.skip_line_comment()
                continue
            
            if self.current_char.isalpha() or self.current_char == '_':
                return self.read_identifier()
            
            if self.current_char.isdigit():
                return self.read_number()
            
            if self.current_char in '"\'':
                return self.read_string()
            
            start_line = self.line
            start_column = self.column
            
            # v3.0: 统一处理双字符运算符（最长匹配原则）
            if self.current_char in '=!<>&|+-':
                peek_char = self.peek()
                if peek_char:
                    candidate = self.current_char + peek_char
                    if candidate in self.double_char_tokens:
                        self.advance()
                        self.advance()
                        return Token(self.double_char_tokens[candidate], candidate, start_line, start_column)
                
                # 单字符处理
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.ASSIGN, '=', start_line, start_column)
                elif self.current_char == '<':
                    self.advance()
                    return Token(TokenType.LESS, '<', start_line, start_column)
                elif self.current_char == '>':
                    self.advance()
                    return Token(TokenType.GREATER, '>', start_line, start_column)
                elif self.current_char == '+':
                    self.advance()
                    return Token(TokenType.PLUS, '+', start_line, start_column)
                elif self.current_char == '-':
                    self.advance()
                    return Token(TokenType.MINUS, '-', start_line, start_column)
                elif self.current_char == '!':
                    self.error(f"非法字符 '!'，期望 '!='")
                    self.advance()
                    continue
                elif self.current_char in '&|':
                    self.error(f"非法字符 '{self.current_char}'，期望 '{self.current_char}{self.current_char}'")
                    self.advance()
                    continue
            
            if self.current_char in self.simple_tokens:
                token_type = self.simple_tokens[self.current_char]
                val = self.current_char
                self.advance()
                return Token(token_type, val, start_line, start_column)
            
            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIVIDE, '/', start_line, start_column)
            
            self.error(f"非法字符 '{self.current_char}'")
            self.advance()
        
        return Token(TokenType.EOF, 'EOF', self.line, self.column)
    
    def tokenize(self):
        """v3.0: 生成器模式 - 按需产出 Token (Lazy Evaluation)
        
        优势：
        1. 内存高效：不需要一次性将所有 Token 加载到内存
        2. 流式处理：适合大文件分析
        3. 架构解耦：与语法分析器的理想接口
        
        用法：
            for token in analyzer.tokenize():
                print(token)
        """
        try:
            while True:
                token = self.get_next_token()
                if token:
                    yield token
                    if token.type == TokenType.EOF:
                        break
                else:
                    break
        except Exception as e:
            print(f"\n分析中断: {e}")
    
    def analyze(self) -> List[Token]:
        """向后兼容的方法 - 一次性返回所有 Token"""
        self.tokens = list(self.tokenize())
        return self.tokens
    
    def print_tokens(self):
        """在终端打印当前已扫描到的所有 Token。

        主要用于：调试、教学演示或人工检查扫描结果是否符合预期。
        """
        print("\n" + "="*60)
        print("Token 序列:")
        print("="*60)
        for i, token in enumerate(self.tokens, 1):
            print(f"{i:3d}. {token}")
    
    def print_symbol_table(self):
        """在终端打印符号表内容。

        每个条目形如 "[index] name"，index 从 0 开始递增。
        """
        print("\n" + "="*60)
        print("符号表 (标识符):")
        print("="*60)
        if self.symbol_table:
            for entry in self.symbol_table:
                print(f"  {entry}")
        else:
            print("  (空)")
    
    def print_constant_table(self):
        """在终端打印常数表内容。

        包括常量的值以及类型（int/float/string 等）。
        """
        print("\n" + "="*60)
        print("常数表:")
        print("="*60)
        if self.constant_table:
            for entry in self.constant_table:
                print(f"  {entry}")
        else:
            print("  (空)")
    
    def print_errors(self):
        """在终端打印扫描过程中收集到的所有错误信息。"""
        if self.errors:
            print("\n" + "="*60)
            print("错误列表:")
            print("="*60)
            for error in self.errors:
                print(f"  {error}")
    
    def save_tokens_to_file(self, filename: str):
        """把 Token 序列、符号表、常数表和错误信息写入到文本文件。

        方便离线查看结果或在报告中引用。
        文件格式保持和终端输出基本一致。
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Token序列\n")
            f.write("="*60 + "\n")
            for i, token in enumerate(self.tokens, 1):
                f.write(f"{i:3d}. {token}\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write("符号表 (标识符)\n")
            f.write("="*60 + "\n")
            if self.symbol_table:
                for entry in self.symbol_table:
                    f.write(f"  {entry}\n")
            else:
                f.write("  (空)\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write("常数表\n")
            f.write("="*60 + "\n")
            if self.constant_table:
                for entry in self.constant_table:
                    f.write(f"  {entry}\n")
            else:
                f.write("  (空)\n")
            
            if self.errors:
                f.write("\n" + "="*60 + "\n")
                f.write("错误列表\n")
                f.write("="*60 + "\n")
                for error in self.errors:
                    f.write(f"  {error}\n")


def main():
    """命令行入口函数。

    用法示例：
        python lexical_analyzer.py input.mini output.txt

    步骤：
    1. 从命令行参数读取源文件路径和输出文件路径；
    2. 打开源文件，读入全部内容；
    3. 创建 LexicalAnalyzer 实例并执行词法分析；
    4. 在终端打印 Token 序列、符号表、常数表和错误列表；
    5. 把同样的信息保存到指定的输出文件中。
    """
    if len(sys.argv) < 2:
        print("用法: python lexical_analyzer.py <源文件路径> [输出文件路径]")
        print("示例: python lexical_analyzer.py test.mini output.txt")
        return
    
    # 命令行第一个参数是源文件路径，第二个参数（可选）是输出文件路径
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "tokens_output.txt"
    
    try:
        # 以 UTF-8 编码读取整个源文件内容
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{input_file}'")
        return
    except Exception as e:
        print(f"错误: 读取文件时出错 - {e}")
        return
    
    print(f"正在分析文件: {input_file}")
    print("="*60)
    
    analyzer = LexicalAnalyzer(source_code)
    analyzer.analyze()
    
    analyzer.print_tokens()
    analyzer.print_symbol_table()
    analyzer.print_constant_table()
    analyzer.print_errors()
    
    analyzer.save_tokens_to_file(output_file)
    print(f"\n结果已保存到: {output_file}")
    
    if analyzer.errors:
        print(f"\n词法分析完成，发现 {len(analyzer.errors)} 个错误")
    else:
        print("\n词法分析成功完成，无错误")


if __name__ == "__main__":
    main()
