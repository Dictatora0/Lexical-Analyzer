#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mini 语言词法分析器 v2.0 - 改进版
改进内容：
1. 支持浮点数
2. 支持字符串常量
3. 支持单行注释 //
4. 符号表/常数表哈希优化
5. 使用分派表消除巨型 IF-ELSE
6. 标准 EOF 处理
7. 错误恢复机制
"""

import sys
from typing import List, Optional, Dict, Union
from enum import IntEnum


class TokenType(IntEnum):
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


class Token:
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
    def __init__(self, name: str, index: int):
        self.name = name
        self.index = index
    
    def __repr__(self):
        return f"[{self.index}] {self.name}"


class ConstantEntry:
    def __init__(self, value: Union[int, float, str], index: int, const_type: str = "int"):
        self.value = value
        self.index = index
        self.const_type = const_type
    
    def __repr__(self):
        return f"[{self.index}] {self.value} ({self.const_type})"


class LexicalAnalyzer:
    MAX_ERRORS = 10
    
    def __init__(self, source_code: str):
        self.source = source_code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source[0] if source_code else None
        
        self.keywords = {
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'int': TokenType.INT,
            'return': TokenType.RETURN
        }
        
        self.simple_tokens = {
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
        }
        
        self.symbol_table: List[SymbolEntry] = []
        self.symbol_map: Dict[str, int] = {}
        
        self.constant_table: List[ConstantEntry] = []
        self.constant_map: Dict[Union[int, float, str], int] = {}
        
        self.tokens: List[Token] = []
        self.errors: List[str] = []
    
    def error(self, message: str):
        error_msg = f"错误 (行 {self.line}, 列 {self.column}): {message}"
        self.errors.append(error_msg)
        print(error_msg)
        
        if len(self.errors) >= self.MAX_ERRORS:
            print(f"\n错误数量已达到上限 ({self.MAX_ERRORS})，停止分析")
            raise Exception(f"错误过多，停止编译")
    
    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
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
        while self.current_char and self.current_char in ' \t\n\r':
            self.advance()
    
    def skip_block_comment(self) -> bool:
        if self.current_char == '/' and self.peek() == '*':
            self.advance()
            self.advance()
            
            while self.current_char:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()
                    self.advance()
                    return True
                self.advance()
            
            self.error("未闭合的块注释")
            return False
        return False
    
    def skip_line_comment(self) -> bool:
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char and self.current_char != '\n':
                self.advance()
            if self.current_char == '\n':
                self.advance()
            return True
        return False
    
    def read_identifier(self) -> Token:
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
        start_line = self.line
        start_column = self.column
        result = ''
        is_float = False
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if is_float:
                    break
                if not self.peek() or not self.peek().isdigit():
                    break
                is_float = True
            result += self.current_char
            self.advance()
        
        if is_float:
            value = float(result)
            index = self.add_to_constant_table(value, "float")
            return Token(TokenType.FLOAT, result, start_line, start_column, index)
        else:
            value = int(result)
            index = self.add_to_constant_table(value, "int")
            return Token(TokenType.INTEGER, result, start_line, start_column, index)
    
    def read_string(self) -> Token:
        start_line = self.line
        start_column = self.column
        quote_char = self.current_char
        self.advance()
        
        result = ''
        while self.current_char and self.current_char != quote_char:
            if self.current_char == '\n':
                self.error(f"字符串常量未闭合")
                break
            
            if self.current_char == '\\':
                self.advance()
                if self.current_char in 'ntr"\'\\':
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
            self.error(f"字符串常量未闭合")
        
        index = self.add_to_constant_table(result, "string")
        return Token(TokenType.STRING, result, start_line, start_column, index)
    
    def add_to_symbol_table(self, name: str) -> int:
        if name in self.symbol_map:
            return self.symbol_map[name]
        
        index = len(self.symbol_table)
        self.symbol_table.append(SymbolEntry(name, index))
        self.symbol_map[name] = index
        return index
    
    def add_to_constant_table(self, value: Union[int, float, str], const_type: str) -> int:
        if value in self.constant_map:
            return self.constant_map[value]
        
        index = len(self.constant_table)
        self.constant_table.append(ConstantEntry(value, index, const_type))
        self.constant_map[value] = index
        return index
    
    def get_next_token(self) -> Optional[Token]:
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
            
            if self.current_char in self.simple_tokens:
                token_type = self.simple_tokens[self.current_char]
                val = self.current_char
                self.advance()
                return Token(token_type, val, start_line, start_column)
            
            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIVIDE, '/', start_line, start_column)
            
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQUAL, '==', start_line, start_column)
                return Token(TokenType.ASSIGN, '=', start_line, start_column)
            
            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.NOT_EQUAL, '!=', start_line, start_column)
                else:
                    self.error(f"非法字符 '!'，期望 '!='")
                    continue
            
            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.LESS_EQUAL, '<=', start_line, start_column)
                return Token(TokenType.LESS, '<', start_line, start_column)
            
            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.GREATER_EQUAL, '>=', start_line, start_column)
                return Token(TokenType.GREATER, '>', start_line, start_column)
            
            self.error(f"非法字符 '{self.current_char}'")
            self.advance()
        
        return Token(TokenType.EOF, 'EOF', self.line, self.column)
    
    def analyze(self) -> List[Token]:
        try:
            while True:
                token = self.get_next_token()
                if token:
                    self.tokens.append(token)
                    if token.type == TokenType.EOF:
                        break
                else:
                    break
        except Exception as e:
            print(f"\n分析中断: {e}")
        
        return self.tokens
    
    def print_tokens(self):
        print("\n" + "="*60)
        print("Token 序列:")
        print("="*60)
        for i, token in enumerate(self.tokens, 1):
            print(f"{i:3d}. {token}")
    
    def print_symbol_table(self):
        print("\n" + "="*60)
        print("符号表 (标识符):")
        print("="*60)
        if self.symbol_table:
            for entry in self.symbol_table:
                print(f"  {entry}")
        else:
            print("  (空)")
    
    def print_constant_table(self):
        print("\n" + "="*60)
        print("常数表:")
        print("="*60)
        if self.constant_table:
            for entry in self.constant_table:
                print(f"  {entry}")
        else:
            print("  (空)")
    
    def print_errors(self):
        if self.errors:
            print("\n" + "="*60)
            print("错误列表:")
            print("="*60)
            for error in self.errors:
                print(f"  {error}")
    
    def save_tokens_to_file(self, filename: str):
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
    if len(sys.argv) < 2:
        print("用法: python lexical_analyzer_v2.py <源文件路径> [输出文件路径]")
        print("示例: python lexical_analyzer_v2.py test.mini output.txt")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "tokens_output_v2.txt"
    
    try:
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
