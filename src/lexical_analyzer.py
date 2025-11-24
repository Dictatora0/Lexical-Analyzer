#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import List, Optional, Tuple
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
    END = 25


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
    def __init__(self, value: int, index: int):
        self.value = value
        self.index = index
    
    def __repr__(self):
        return f"[{self.index}] {self.value}"


class LexicalAnalyzer:
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
        
        self.symbol_table: List[SymbolEntry] = []
        self.constant_table: List[ConstantEntry] = []
        self.tokens: List[Token] = []
        self.errors: List[str] = []
    
    def error(self, message: str):
        error_msg = f"错误 (行 {self.line}, 列 {self.column}): {message}"
        self.errors.append(error_msg)
        print(error_msg)
    
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
    
    def skip_comment(self):
        if self.current_char == '/' and self.peek() == '*':
            self.advance()
            self.advance()
            
            while self.current_char:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()
                    self.advance()
                    return True
                self.advance()
            
            self.error("未闭合的注释")
            return False
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
        
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        value = int(result)
        index = self.add_to_constant_table(value)
        return Token(TokenType.INTEGER, result, start_line, start_column, index)
    
    def add_to_symbol_table(self, name: str) -> int:
        for entry in self.symbol_table:
            if entry.name == name:
                return entry.index
        
        index = len(self.symbol_table)
        self.symbol_table.append(SymbolEntry(name, index))
        return index
    
    def add_to_constant_table(self, value: int) -> int:
        for entry in self.constant_table:
            if entry.value == value:
                return entry.index
        
        index = len(self.constant_table)
        self.constant_table.append(ConstantEntry(value, index))
        return index
    
    def get_next_token(self) -> Optional[Token]:
        while self.current_char:
            if self.current_char in ' \t\n\r':
                self.skip_whitespace()
                continue
            
            if self.current_char == '/' and self.peek() == '*':
                self.skip_comment()
                continue
            
            if self.current_char.isalpha() or self.current_char == '_':
                return self.read_identifier()
            
            if self.current_char.isdigit():
                return self.read_number()
            
            start_line = self.line
            start_column = self.column
            
            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+', start_line, start_column)
            
            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-', start_line, start_column)
            
            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MULTIPLY, '*', start_line, start_column)
            
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
            
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LEFT_PAREN, '(', start_line, start_column)
            
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RIGHT_PAREN, ')', start_line, start_column)
            
            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LEFT_BRACE, '{', start_line, start_column)
            
            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RIGHT_BRACE, '}', start_line, start_column)
            
            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';', start_line, start_column)
            
            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',', start_line, start_column)
            
            if self.current_char == '#':
                self.advance()
                return Token(TokenType.END, '#', start_line, start_column)
            
            self.error(f"非法字符 '{self.current_char}'")
            self.advance()
        
        return None
    
    def analyze(self) -> List[Token]:
        while True:
            token = self.get_next_token()
            if token:
                self.tokens.append(token)
                if token.type == TokenType.END:
                    break
            else:
                break
        
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
        print("用法: python lexical_analyzer.py <源文件路径> [输出文件路径]")
        print("示例: python lexical_analyzer.py test_correct.mini output.txt")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "tokens_output.txt"
    
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
