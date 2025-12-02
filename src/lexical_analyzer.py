#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Mini 语言词法分析器。

功能概述：
1. 支持整数、浮点数和科学计数法 (1.2e-5, 3.0E+10)
2. 支持字符串常量
3. 支持单行注释 // 和块注释 /* ... */
4. 支持逻辑运算符 (&&, ||) 和自增自减 (++, --)
5. 精确的 Tab 处理（列号计算）
6. 维护符号表和常数表，并可输出 token、符号表和常数表到文件
7. 提供生成器模式按需产出 token
"""

import sys
from typing import List, Optional, Dict, Union, Tuple
from enum import IntEnum

# TokenType 概览（按类别分组）：
# - 关键字：IF, ELSE, WHILE, INT, RETURN
# - 算术/比较：PLUS, MINUS, MULTIPLY, DIVIDE, ASSIGN, EQUAL, NOT_EQUAL,
#             LESS, LESS_EQUAL, GREATER, GREATER_EQUAL
# - 界限符：LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE, SEMICOLON, COMMA
# - 标识/字面量：IDENTIFIER, INTEGER, FLOAT, STRING, EOF
# - 扩展运算符：AND(&&), OR(||), INCREMENT(++), DECREMENT(--)，采用最长匹配
class TokenType(IntEnum):
    """Mini 语言中所有 token 类型的枚举。"""
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

    # 额外的逻辑运算符和自增自减运算符
    AND = 29          # &&
    OR = 30           # ||
    INCREMENT = 31    # ++
    DECREMENT = 32    # --


class Token:
    """词法单元，表示源代码中的一个记号。"""

    def __init__(self, token_type: int, value: str, line: int, column: int, attr_index: int = -1):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
        self.attr_index = attr_index # 指向符号表/常数表索引，默认 -1
    
    def __repr__(self):
        if self.attr_index >= 0:
            return f"<{self.type}, '{self.value}', Line:{self.line}, Col:{self.column}, Index:{self.attr_index}>"
        else:
            return f"<{self.type}, '{self.value}', Line:{self.line}, Col:{self.column}>"


class SymbolEntry:
    """符号表条目，记录标识符及其索引。"""

    def __init__(self, name: str, index: int):
        self.name = name
        self.index = index
    
    def __repr__(self):
        return f"[{self.index}] {self.name}"


class ConstantEntry:
    """常数表条目，记录字面量值、索引及类型。"""

    def __init__(self, value: Union[int, float, str], index: int, const_type: str = "int"):
        self.value = value
        self.index = index
        self.const_type = const_type
    
    def __repr__(self):
        return f"[{self.index}] {self.value} ({self.const_type})"


class LexicalAnalyzer:
    """Mini 语言词法分析器，负责扫描源代码并生成 token。"""
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
        # Tab 宽度固定为 4，用于计算列号，采用制表位 (tab stop) 计算方式
        self.tab_width = 4
        
        # 关键字表：扫描到对应单词时直接映射为关键字 Token
        self.keywords = {
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'int': TokenType.INT,
            'return': TokenType.RETURN
        }
        
        # 双字符运算符映射表，采用最长匹配优先
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
        
        # 说明：'/' 不放入此表，因其既可能是除号也可能是注释起始，
        # 统一在 get_next_token 中根据上下文（前瞻）进行特殊处理。
        self.simple_tokens = {
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '*': TokenType.MULTIPLY,
        }
        
        self.symbol_table: List[SymbolEntry] = []  # 顺序表：保存唯一标识符条目（索引即符号ID）
        self.symbol_map: Dict[str, int] = {}       # name -> index 映射，用于去重/快速查找 O(1)
        
        self.constant_table: List[ConstantEntry] = []  # 顺序表：保存唯一字面量（含类型）
        self.constant_map: Dict[Tuple[str, Union[int, float, str]], int] = {}  # (type, value) -> index；区分 int 1 与 float 1.0
        
        self.tokens: List[Token] = []  # 若使用 analyze() 会填充完整 Token 列表；生成器模式可不使用
        self.errors: List[str] = []    # 扫描错误消息集合（最多记录 MAX_ERRORS 条提示）
    
    def error(self, message: str):
        """记录错误并尽量不中断扫描。
        
        Args:
            message: 错误描述文本。
        Side Effects:
            - 追加到 self.errors 并立即打印。
            - 首次达到 MAX_ERRORS 时给出提示；为收集更多错误不抛出异常。
        """
        # 统一的错误处理入口：
        # 1. 把错误信息记录到 errors 列表，方便在末尾集中输出；
        # 2. 立刻打印到终端，便于调试时第一时间看到问题；
        # 3. 不直接抛异常，而是尽量继续往后扫描，收集更多错误信息。
        error_msg = f"错误 (行 {self.line}, 列 {self.column}): {message}"
        self.errors.append(error_msg)
        print(error_msg)
        
        # 在错误数量第一次达到上限时给出提示，不中断后续分析
        if len(self.errors) == self.MAX_ERRORS:
            print(f"\n警告: 错误数量已达到 {self.MAX_ERRORS} 个，继续分析...")
    
    def advance(self):
        """前进一个字符并维护精确行/列。
        
        行为：
        - 遇 '\n'：line+1, column=1
        - 遇 '\t'：按制表位对齐（见下方推导注释）
        - 其他：column+1
        Returns: None
        """
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        elif self.current_char == '\t':
            # 计算下一个制表位 (Tab Stop)
            # 推导（1基列号 -> 0基对齐 -> 回到1基）：
            # 设 z = column - 1（0基），制表位在 0, w, 2w, ... 处（w=self.tab_width）。
            # 下一制表位的 0 基位置：next0 = ((z // w) + 1) * w（严格大于 z 的最小 w 的倍数）。
            # 需要前进的列数 Δ = next0 - z = w - (z % w) = w - ((column - 1) % w)。
            # 因此 1 基实现可用增量式：column += w - ((column - 1) % w)。
            self.column += (self.tab_width - (self.column - 1) % self.tab_width)
        else:
            self.column += 1
        
        self.pos += 1
        if self.pos < len(self.source):
            self.current_char = self.source[self.pos]
        else:
            self.current_char = None
    
    def peek(self, offset: int = 1) -> Optional[str]:
        """前瞻 offset 个字符但不消耗。
        
        Args:
            offset: 正偏移，默认 1。
        Returns:
            对应字符或 None（越界）。
        """
        peek_pos = self.pos + offset
        if peek_pos < len(self.source):
            return self.source[peek_pos]
        return None
    
    def skip_whitespace(self):
        """跳过空白字符（空格/Tab/换行/回车）。
        
        Returns: None
        Side Effects: 指针移动到下一个非空白字符。
        """
        while self.current_char and self.current_char in ' \t\n\r':
            self.advance()
    
    def skip_block_comment(self) -> bool:
        """尝试跳过块注释 /* ... */。
        
        Returns:
            True  已识别并跳过
            False 非块注释起始或未闭合（未闭合会记录错误）
        Side Effects: 更新位置；未闭合时调用 error()。
        """
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
        """尝试跳过 // 单行注释，直到并含换行。
        
        Returns: True 若当前是行注释起始，否则 False。
        Side Effects: 前进至下一行起始。
        """
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char and self.current_char != '\n':
                self.advance()
            if self.current_char == '\n':
                self.advance()
            return True
        return False
    
    def read_identifier(self) -> Token:
        """读取标识符或关键字。
        
        Returns:
            若在关键字表中，返回对应关键字 Token；否则返回 IDENTIFIER，附符号表索引。
        """
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
        """读取整数/小数/科学计数法字面量。
        
        规则：
        - 小数点至多 1 个；点后必须有数字（例如 "1." 不视为浮点，点保留给后续处理）。
        - 可选指数 e/E，后接可选 +/- 与至少一位数字。
        语言规范：不允许“尾点小数”（如 1.），需要写作 1.0。
        
        Returns:
            INTEGER 或 FLOAT；指数格式错误时仍返回 FLOAT，attr_index=-1，并记录错误。
        """
        # 整数、小数和科学计数法统一在这里处理
        # start_line/start_column 用来在出错时给出准确位置
        start_line = self.line
        start_column = self.column
        result = ''
        is_float = False
        
        # 读取整数部分和小数部分
        # 规则：
        # - 允许至多一个小数点；第二次遇到 '.' 直接停止数字读取（交给后续逻辑处理）。
        # - 点后必须有数字；否则不把 '.' 吸收（例如 "1." 会在此处停止为 "1"，
        #   后续把 '.' 当作单独字符处理），以避免错误的浮点格式。
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if is_float:
                    break
                if not self.peek() or not self.peek().isdigit():
                    break
                is_float = True
            result += self.current_char
            self.advance()
        
        # 处理科学计数法指数部分 (e 或 E)，例如 1.23e-4 或 3E+8
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
        
        # 存入常数表：浮点和整数分别记录类型，后续可按类型做不同处理
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
        r"""读取字符串字面量（支持 ' 与 ").
        
        支持转义：\n, \t, \r, \", \, \\。
        错误：未闭合时会在发生位置与函数结束处各报一次，便于定位。
        
        Returns: STRING（带常数表索引）。
        """
        start_line = self.line
        start_column = self.column
        quote_char = self.current_char
        self.advance()
        
        result = ''
        while self.current_char and self.current_char != quote_char:
            if self.current_char == '\n':
                # 遇到换行说明引号没有闭合：
                # 这里先报错并终止本字符串读取；循环之后若未见闭合引号，
                # 还会再次报错一次，这样做可以在错误位置和结束位置都给出提示，
                # 便于定位（必要时可改为仅一次提示）。
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
        """符号表去重，返回索引。
        
        语法阶段可仅保存整数索引，无需重复存储完整标识符字符串。
        """
        if name in self.symbol_map:
            return self.symbol_map[name]
        
        index = len(self.symbol_table)
        self.symbol_table.append(SymbolEntry(name, index))
        self.symbol_map[name] = index
        return index
    
    def add_to_constant_table(self, value: Union[int, float, str], const_type: str) -> int:
        """常数表去重并返回索引。
        
        相同“类型+值”的字面量只保留一份以节省空间；
        通过使用 (const_type, value) 作为键，严格区分 int 1 与 float 1.0。
        """
        key: Tuple[str, Union[int, float, str]] = (const_type, value)
        if key in self.constant_map:
            return self.constant_map[key]
        
        index = len(self.constant_table)
        self.constant_table.append(ConstantEntry(value, index, const_type))
        self.constant_map[key] = index
        return index
    
    def get_next_token(self) -> Optional[Token]:
        """返回下一个 Token（主扫描循环）。
        
        流程：跳空白/注释 → 标识符/数字/字符串 → 双字符运算符（最长匹配）→ 单字符 → 错误恢复。
        Returns: 下一个 Token；源尽时返回 EOF。
        Side Effects: 可能记录错误并继续扫描。
        """
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
            
            # 统一处理双字符运算符（最长匹配原则）：
            # 先尝试两个字符的组合（== != <= >= && || ++ --），若匹配则消费两字符；
            # 否则回退到单字符分支；对于单独的 '!'、'&'、'|'，按语言定义视为错误并提示
            # 应为 '!='、'&&'、'||'，以帮助使用者快速定位问题。
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
        """按需产出 Token 的生成器。
        
        Yields: Token（包含 EOF）。
        Side Effects: 调用 get_next_token()，可能记录错误。
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
        """一次性收集全部 Token。
        
        Returns: List[Token]（最后一项为 EOF）。
        Side Effects: 填充 self.tokens。
        """
        self.tokens = list(self.tokenize())
        return self.tokens
    
    def print_tokens(self):
        """在终端打印已扫描 Token 列表（含序号）。"""
        print("\n" + "="*60)
        print("Token 序列:")
        print("="*60)
        for i, token in enumerate(self.tokens, 1):
            print(f"{i:3d}. {token}")
    
    def print_symbol_table(self):
        """在终端打印符号表（索引与标识符）。"""
        print("\n" + "="*60)
        print("符号表 (标识符):")
        print("="*60)
        if self.symbol_table:
            for entry in self.symbol_table:
                print(f"  {entry}")
        else:
            print("  (空)")
    
    def print_constant_table(self):
        """在终端打印常数表（索引、值、类型）。"""
        print("\n" + "="*60)
        print("常数表:")
        print("="*60)
        if self.constant_table:
            for entry in self.constant_table:
                print(f"  {entry}")
        else:
            print("  (空)")
    
    def print_errors(self):
        """在终端打印扫描过程中收集到的错误列表。"""
        if self.errors:
            print("\n" + "="*60)
            print("错误列表:")
            print("="*60)
            for error in self.errors:
                print(f"  {error}")
    
    def save_tokens_to_file(self, filename: str):
        """将 Token、符号表、常数表与错误列表写入文本文件。
        
        输出结构：
        - Token序列（带序号与位置信息）
        - 符号表 (标识符)
        - 常数表
        - 错误列表（如有）
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
    
    提示：输出文件包含四部分——Token序列 / 符号表(标识符) / 常数表 / 错误列表(可选)。
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
    print("输出文件结构: Token序列 / 符号表(标识符) / 常数表 / 错误列表(可选)")
    
    if analyzer.errors:
        print(f"\n词法分析完成，发现 {len(analyzer.errors)} 个错误")
    else:
        print("\n词法分析成功完成，无错误")


if __name__ == "__main__":
    main()
