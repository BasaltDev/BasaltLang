# Basalt Interpreter - Copyright (c) 2026 BasaltDev
# Licensed under the MIT License.

import colorama
import os
import time
import sys
import subprocess
import random
from definitions import *

argv = sys.argv
argc = len(argv)
parent_folder = None

class Lexer:
    def __init__(self, source_code, keywords=[]):
        self.source_code = source_code
        self.position = 0
        self.current_char = self.source_code[self.position]
        self.tokens = []
        self.keywords = keywords

    def advance(self):
        self.position += 1
        if self.position >= len(self.source_code):
            self.current_char = None
        else:
            self.current_char = self.source_code[self.position]
    
    def peek(self, amount=1):
        position = self.position + amount
        if position >= len(self.source_code):
            return None
        return self.source_code[position]
    
    def get_identifier(self):
        output = ""
        while self.current_char is not None and (self.current_char.isalpha() or self.current_char.isdigit() or self.current_char == "_"):
            output += self.current_char
            self.advance()
        self.position -= 1
        return output
    
    def get_string(self):
        output = ""
        self.advance()
        while self.current_char is not None:
            if self.current_char == '"':
                self.position -= 2
                self.advance()
                if self.current_char != '\\':
                    self.advance()
                    break
                else:
                    output = output[:-1]
                    self.advance()
            output += self.current_char
            self.advance()
        return output
    
    def get_number(self):
        output = ""
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == "."):
            output += self.current_char
            self.advance()
        self.position -= 1
        if output.count(".") > 0:
            output = float(output)
        else:
            output = int(output)
        return output

    def tokenize(self):
        comment = False
        multiline_comment = False
        while self.current_char is not None:
            if comment:
                if self.current_char == "\n":
                    comment = False
                    self.tokens.append(("NEWLINE", "\n"))
                self.advance()
                continue
            elif multiline_comment:
                if self.current_char == ">":
                    if self.peek(-1) == "-" and self.peek(-2) == "-" and self.peek(-3) == "-" and self.peek(-4) == "-":
                        multiline_comment = False
                elif self.current_char == "\n":
                    self.tokens.append(("NEWLINE", "\n"))
                self.advance()
                continue
            if self.current_char.isalpha() or self.current_char == "_":
                identifier = self.get_identifier()
                prefix = "IDENTIFIER"
                if identifier in self.keywords:
                    prefix = "KEYWORD"
                elif identifier in ("True", "False"):
                    prefix = "BOOLEAN"
                    if identifier == "True":
                        identifier = True
                    else:
                        identifier = False
                self.tokens.append((prefix, identifier))
            elif self.current_char == "<":
                if self.peek() == "-" and self.peek(2) == "-":
                    if self.peek(3) == "-" and self.peek(4) == "-":
                        multiline_comment = True
                    else:
                        comment = True
                elif self.peek() == "=":
                    self.tokens.append(("LOGIC", "<="))
                    self.advance()
                else:
                    self.tokens.append(("LOGIC", "<"))
            elif self.current_char == ">":
                if self.peek(-1) == "-" and self.peek(-2) == "-":
                    comment = True
                    self.tokens = self.tokens[:-1]
                elif self.peek() == "=":
                    self.tokens.append(("LOGIC", ">="))
                    self.advance()
                else:
                    self.tokens.append(("LOGIC", ">"))
            elif self.current_char == "!":
                if self.peek() == "=":
                    self.tokens.append(("LOGIC", "!="))
                    self.advance()
            elif self.current_char == '"':
                string = self.get_string()
                self.tokens.append(("STRING", string))
            elif self.current_char.isdigit():
                number = self.get_number()
                self.tokens.append(("NUMBER", number))
            elif self.current_char in "()":
                self.tokens.append(("PARENTHESIS", self.current_char))
            elif self.current_char in "[]":
                self.tokens.append(("SQUARE", self.current_char))
            elif self.current_char in "{}":
                self.tokens.append(("CURLY", self.current_char))
            elif self.current_char == "=":
                if self.peek() == "=":
                    self.tokens.append(("LOGIC", "=="))
                    self.advance()
                else:
                    self.tokens.append(("ASSIGNMENT", "="))
            elif self.current_char == "+":
                if self.peek() == "=":
                    self.tokens.append(("ARITHMETIC_ASSIGNMENT", "+="))
                    self.advance()
                elif self.peek() == "+":
                    self.tokens.append(("CREMENTATION", "++"))
                    self.advance()
            elif self.current_char == "-":
                if self.peek() == "=":
                    self.tokens.append(("ARITHMETIC_ASSIGNMENT", "-="))
                    self.advance()
                elif self.peek() == "-":
                    self.tokens.append(("CREMENTATION", "--"))
                    self.advance()
                elif self.peek() == ">":
                    self.tokens.append(("RETURN_OPERATOR", "->"))
                    self.advance()
                elif self.peek().isdigit():
                    self.advance()
                    number = self.get_number()
                    self.tokens.append(("NUMBER", -number))
            elif self.current_char == "*":
                if self.peek() == "=":
                    self.tokens.append(("ARITHMETIC_ASSIGNMENT", "*="))
                    self.advance()
            elif self.current_char == "/":
                if self.peek() == "=":
                    self.tokens.append(("ARITHMETIC_ASSIGNMENT", "/="))
                    self.advance()
                elif self.peek() == "/":
                    if self.peek(2) == "=":
                        self.tokens.append(("ARITHMETIC_ASSIGNMENT", "//="))
                        self.advance()
                        self.advance()
            elif self.current_char == "%":
                if self.peek() == "=":
                    self.tokens.append(("ARITHMETIC_ASSIGNMENT", "%="))
                    self.advance()
            elif self.current_char == "^":
                if self.peek() == "=":
                    self.tokens.append(("ARITHMETIC_ASSIGNMENT", "^="))
                    self.advance()
            elif self.current_char == ",":
                self.tokens.append(("COMMA", ","))
            elif self.current_char == ".":
                self.tokens.append(("PERIOD", "."))
            elif self.current_char == ";":
                self.tokens.append(("SEMICOLON", ";"))
            elif self.current_char == ":":
                self.tokens.append(("COLON", ":"))
            elif self.current_char == "@":
                if self.peek().isalpha() or self.peek() == "_":
                    self.advance()
                    identifier = self.get_identifier()
                    self.tokens.append(("MODIFIER", identifier))
                else:
                    self.tokens.append(("MONKEY", "@"))
            elif self.current_char == "$":
                self.tokens.append(("DOLLAR", "$"))
            elif self.current_char == "\n":
                self.tokens.append(("NEWLINE", "\n"))
            self.advance()
        return self.tokens
    
class Interpreter:
    def __init__(self, tokens, repl=False):
        global argv
        global parent_folder
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[self.position]
        self.variables = {
            "argv": {
                "value": argv[1:],
                "mutable": False
            },
            "argc": {
                "value": argc - 2,
                "mutable": False
            },
            "null": {
                "value": None,
                "mutable": False
            },
        }
        self.classes = {}
        self.class_variables = {} # yes, special type of variable for classes, holy shit :O
        self.broken = False
        self.functions = {}
        self.curly_count = 0
        self.return_value = None
        self.if_statement_truth_table = {

        }
        self.error_output = ""
        self.line = 1
        self.repl = repl

    def advance(self):
        self.position += 1
        if self.position >= len(self.tokens):
            self.current_token = None
        else:
            self.current_token = self.tokens[self.position]
    
    def peek(self, amount=1):
        position = self.position + amount
        if position >= len(self.tokens):
            return None
        else:
            return self.tokens[position]

    def peek_until(self, delimiter: tuple):
        peeked = []
        while self.current_token != delimiter:
            peeked.append(self.current_token)
            self.advance()
        return peeked
        
    def error(self, error_message, line):
        red = colorama.Fore.RED
        yellow = colorama.Fore.YELLOW
        reset = colorama.Fore.RESET
        print(f"{red}Error at line {yellow}{line}{red}: {error_message}{reset}")
        self.error_output = error_message
        sys.exit(1)
    
    def issue(self, issue_message, line):
        yellow = colorama.Fore.YELLOW
        reset = colorama.Fore.RESET
        print(f"{yellow}Issue at line {line}: {issue_message}{reset}")

    def skip_block(self):
        brace_count = 0
        while self.current_token is not None:
            if self.current_token[0] == "NEWLINE":
                self.line += 1
            if self.current_token[1] == "{":
                brace_count += 1
                self.curly_count += 1
            elif self.current_token[1] == "}":
                brace_count -= 1
                self.curly_count -= 1
                if brace_count == 0:
                    self.advance()
                    break
            self.advance()
        self.curly_count -= 1
    
    def parse_condition(self, condition):
        # translate into something easier to understand
        idx = 0
        statement = []
        for item in condition:
            item_type, item_value = item[0], item[1]
            if item_type == "LOGIC":
                left_type, left_value = condition[idx - 1][0], condition[idx - 1][1]
                right_type, right_value = condition[idx + 1][0], condition[idx + 1][1]
                if left_type == "IDENTIFIER":
                    left_value = self.variables[left_value]["value"]
                if right_type == "IDENTIFIER":
                    right_value = self.variables[right_value]["value"]
                if type(left_value) == str:
                    left_value = left_value.replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t").replace("\b", "\\b")
                    left_value = left_value.replace("\\", "")
                    left_value = f"\"{left_value}\""
                if type(right_value) == str:
                    right_value = right_value.replace("\"", "\\\"").replace("\n", "\\n").replace("\t", "\\t").replace("\b", "\\b")
                    right_value = right_value.replace("\\", "")
                    right_value = f"\"{right_value}\""
                statement.append([left_value, item_value, right_value])
            elif item_value in ('and', 'or', 'not'):
                statement.append(item_value)
            idx += 1
        # convert it into python logic
        parsed = ""
        for item in statement:
            if type(item) == list:
                for i in item:
                    parsed += str(i).replace("\n", "") + " "
            else:
                parsed += str(item) + " "
        parsed = parsed.replace('"""', '""')
        evaluated = eval(parsed)
        return evaluated

    def skip_block_function(self, name, params, line, class_method=False, tokens=[], indx=0):
        brace_count = 0
        if not class_method:
            function = []
            while self.current_token is not None:
                if self.current_token[0] == "NEWLINE":
                    self.line += 1
                else:
                    function.append(self.current_token)
                if self.current_token[1] == "{":
                    brace_count += 1
                    self.curly_count += 1
                elif self.current_token[1] == "}":
                    brace_count -= 1
                    self.curly_count -= 1
                    if brace_count == 0:
                        self.advance()
                        break
                self.advance()
            self.curly_count -= 1
            self.functions[name] = {
                "tokens": function[1:-1],
                "params": params,
                "line": line
            }
            self.position -= 2
            self.advance()
        else:
            function_tokens = []
            token = tokens[0]
            idx = 0
            brace_count = 1
            while token is not None:
                indx+=1
                if token[0] == "NEWLINE":
                    self.line += 1
                else:
                    function_tokens.append(token)
                if token[1] == "{":
                    brace_count += 1
                    self.curly_count += 1
                elif token[1] == "}":
                    brace_count -= 1
                    self.curly_count -= 1
                    if brace_count == 0:
                        idx += 1
                        break
                idx += 1
                if idx >= len(tokens):
                    token = None
                    continue
                token = tokens[idx]
            return function_tokens[:-1], indx
    
    def skip_block_repeat(self, amount):
        brace_count = 0
        repeat = []
        while self.current_token is not None:
            if self.current_token[0] == "NEWLINE":
                self.line += 1
            else:
                repeat.append(self.current_token)
            if self.current_token[1] == "{":
                brace_count += 1
                self.curly_count += 1
            elif self.current_token[1] == "}":
                brace_count -= 1
                self.curly_count -= 1
                if brace_count == 0:
                    self.advance()
                    break
            self.advance()
        self.curly_count -= 1
        self.position -= 2
        for _ in range(0, amount):
            new_interpreter = Interpreter(repeat)
            new_interpreter.interpret(variables=self.variables, functions=self.functions, line=self.line)
            if new_interpreter.broken:
                break
        self.advance()
    
    def skip_block_foreach(self, condition):
        brace_count = 0
        foreach = []
        while self.current_token is not None:
            if self.current_token[0] == "NEWLINE":
                self.line += 1
            else:
                foreach.append(self.current_token)
            if self.current_token[1] == "{":
                brace_count += 1
                self.curly_count += 1
            elif self.current_token[1] == "}":
                brace_count -= 1
                self.curly_count -= 1
                if brace_count == 0:
                    self.advance()
                    break
            self.advance()
        self.curly_count -= 1
        self.position -= 2
        if condition[1] != ("KEYWORD", "in"):
            self.error("missing 'in' keyword between foreach values (shocking, i know)", self.line)
        left = condition[0]
        right = condition[2]
        if right[0] == "IDENTIFIER":
            right = self.variables[right[1]]["value"]
        variable = left
        if variable[0] == "IDENTIFIER":
            variable = variable[1]
        foreach = foreach[5:-1]
        for i in right:
            variables = self.variables
            variables[variable] = {
                "value": i,
                "mutable": True
            }
            new_interpreter = Interpreter(foreach)
            new_interpreter.interpret(variables=variables, functions=self.functions, line=self.line)
            if new_interpreter.broken:
                break
        self.advance()
    
    def skip_block_while(self, condition):
        brace_count = 0
        repeat = []
        while self.current_token is not None:
            if self.current_token[0] == "NEWLINE":
                self.line += 1
            else:
                repeat.append(self.current_token)
            if self.current_token[1] == "{":
                brace_count += 1
                self.curly_count += 1
            elif self.current_token[1] == "}":
                brace_count -= 1
                self.curly_count -= 1
                if brace_count == 0:
                    self.advance()
                    break
            self.advance()
        self.curly_count -= 1
        self.position -= 2
        while self.parse_condition(condition):
            new_interpreter = Interpreter(repeat)
            new_interpreter.interpret(variables=self.variables, functions=self.functions, line=self.line)
            if new_interpreter.broken:
                break
        self.advance()
    
    def skip_block_class(self, name, params, line):
        brace_count = 0
        class_ = []
        while self.current_token is not None:
            if self.current_token[0] == "NEWLINE":
                self.line += 1
            else:
                class_.append(self.current_token)
            if self.current_token[1] == "{":
                brace_count += 1
                self.curly_count += 1
            elif self.current_token[1] == "}":
                brace_count -= 1
                self.curly_count -= 1
                if brace_count == 0:
                    self.advance()
                    break
            self.advance()
        methods = {}
        self.advance()
        self.advance()
        idx = 0
        while idx < len(class_):
            token = class_[idx]
            if token == ("KEYWORD", "fn"):
                if idx >= len(class_):
                    break
                idx += 1
                nam = class_[idx][1]
                pars = []
                if class_[idx] == ("PARENTHESIS", "(") or class_[idx] == ("SQUARE", "["):
                    idx += 1
                    pars = []
                    while 1==1:
                        idx += 1
                        if class_[idx] == ("PARENTHESIS", ")") or class_[idx] == ("SQUARE", "]"):
                            break
                        else:
                            pars.append(class_[idx])
                while 1==1:
                    if class_[idx] == ("CURLY", "{"):
                        idx += 1
                        break
                    idx += 1
                method, idx = self.skip_block_function(nam, pars, 0, class_method=True, tokens=class_[idx:], indx=idx)
                methods[nam] = method
            else:
                idx += 1
        self.curly_count -= 1
        self.classes[name] = {
            "methods": methods,
            "params": params,
            "self": {},
            "line": line
        }
        if not methods.get("init"):
            self.error(f"missing init() method", f"\b\b\b\b\bclass '{name}'")
        self.position -= 2
        self.advance()
    
    def interpret(self, variables=None, functions=None, line=None, in_function=False, importing=False, cls=False, classe=None):
        if variables:
            self.variables = variables
        if functions:
            self.functions = functions
        if line:
            self.line = line
        while self.current_token is not None:
            current_token_type = self.current_token[0]
            current_token_value = self.current_token[1]
            if current_token_type == "NEWLINE":
                self.line += 1
            elif current_token_type == "KEYWORD":
                if current_token_value in ("print", "println", "printf"):
                    next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                    if next_token_type == "PARENTHESIS" and next_token_value == "(":
                        print_type, print_value = self.peek(2)[0], self.peek(2)[1]
                        expected_parenthesis_type, expected_parenthesis_value = self.peek(3)[0], self.peek(3)[1]
                        if expected_parenthesis_type != "PARENTHESIS" or expected_parenthesis_value != ")":
                            self.error("missing closing parenthesis", self.line)
                        if print_type != "IDENTIFIER":
                            print_value = print_value.replace("\\n", "\n").replace("\\t", "\t").replace("\\b", "\b")
                            ending=''
                            if current_token_value == "println":
                                ending = '\n'
                            if current_token_value == "printf":
                                new_string = ""
                                bracket_buffer = ""
                                bracketing = False
                                idx = 0
                                for char in print_value:
                                    if bracketing:
                                        if char == "]":
                                            bracketing = False
                                            if not self.variables.get(bracket_buffer):
                                                self.error(f"inexistent variable '{bracket_buffer}'", self.line)
                                            value = self.variables[bracket_buffer]["value"]
                                            if value == None:
                                                value = "[?]"
                                                self.issue(f"variable '{bracket_buffer}' is undefined", self.line)
                                            elif type(value) == list:
                                                list_string = "["
                                                for i in value:
                                                    if type(i) == str:
                                                        i = f'"{i}"'
                                                    list_string += str(i) + " "
                                                if list_string != "[":
                                                    list_string = list_string[:-1]
                                                list_string += "]"
                                                value = list_string
                                            elif type(value) == dict:
                                                dict_string = "{"
                                                for k,v in value.items():
                                                    if type(v) == str:
                                                        v = f'"{v}"'
                                                    dict_string += f'"{k}": {v} '
                                                dict_string = dict_string[:-1]
                                                dict_string += "}"
                                                value = dict_string
                                            new_string += str(value)
                                            bracket_buffer = ""
                                            continue
                                        bracket_buffer += char
                                        continue
                                    if char == '[' and not print_value[idx - 1] == "\\":
                                        bracketing = True
                                        continue
                                    else:
                                        new_string += char
                                    idx += 1
                                print_value = new_string
                            print(print_value, end=ending)
                        else:
                            self.error("you can't print a variable name directly, you have to put it in a format print ('printf(\"[variable_name]\")')", self.line)
                    else:
                        self.error("missing opening parenthesis", self.line)
                elif current_token_value == "let":
                    next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                    mutable = False
                    index = 0
                    if next_token_type == "KEYWORD":
                        if next_token_value == "mut":
                            mutable = True
                            index = 1
                        if next_token_value == "undef":
                            variable_name = self.peek(2)[1]
                            self.variables[variable_name] = {
                                "value": None,
                                "mutable": True
                            }
                            self.advance()
                            continue
                    variable_name = self.peek(index + 1)[1]
                    peek = self.peek(index + 1)
                    var_val = None
                    if peek != None:
                        next_token_type, next_token_value = self.peek(index + 2)[0], self.peek(index + 2)[1]
                    else:
                        next_token_type, next_token_value = None, None
                    if next_token_type != "ASSIGNMENT" and next_token_value != "=":
                        self.error("missing assignment operator, if you want an undefined variable you type undef before the variable name", self.line)
                    else:
                        next_token_type, next_token_value = self.peek(index + 3)[0], self.peek(index + 3)[1]
                        if next_token_type == "IDENTIFIER":
                            var_val = next_token_value
                            next_token_value = self.variables[next_token_value]["value"]
                        elif next_token_type == "SQUARE" and next_token_value == "[":
                            self.advance(); self.advance(); self.advance()
                            value = self.peek_until(("SQUARE", "]"))
                            if value[0] == ("ASSIGNMENT", "="):
                                value = value[1:]
                            if value[0] == ("SQUARE", "["):
                                value = value[1:]
                            new_value = []
                            idx = 0
                            for val in value:
                                new_val = val[1]
                                if val[0] == "IDENTIFIER":
                                    new_val = self.variables[val[1]]["value"]
                                new_value.append(new_val)
                            next_token_value = new_value
                        elif next_token_type == "CURLY" and next_token_value == "{":
                            self.advance(); self.advance(); self.advance()
                            value = self.peek_until(("CURLY", "}"))
                            if value[0] == ("ASSIGNMENT", "="):
                                value = value[1:]
                            if value[0] == ("CURLY", "{"):
                                value = value[1:]
                            new_value = []
                            idx = 0
                            dictionary = {}
                            for val in value:
                                new_val = val[1]
                                if val[0] == "COLON":
                                    left = value[idx - 1]
                                    right = value[idx + 1]
                                    if left[0] == "IDENTIFIER":
                                        left = self.variables[left[1]]["value"]
                                    else:
                                        left = left[1]
                                    if right[0] == "IDENTIFIER":
                                        right = self.variables[right[1]]["value"]
                                    else:
                                        right = right[1]
                                    dictionary[left] = right
                                    # new_val = self.variables[val[1]]["value"]
                                idx += 1
                            next_token_value = dictionary
                        self.variables[variable_name] = {
                            "value": next_token_value,
                            "mutable": mutable
                        }
                        if var_val == "argv" or type(next_token_value) not in (list, dict):
                            self.advance(); self.advance(); self.advance()
                elif current_token_value in ("mut", "immut"):
                    next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                    if next_token_type != "PARENTHESIS" and next_token_value != "(":
                        self.error(f"missing opening parenthesis for {current_token_value}() function", self.line)
                    next_token_type, next_token_value = self.peek(3)[0], self.peek(3)[1]
                    if next_token_type != "PARENTHESIS" and next_token_value != ")":
                        self.error(f"missing closing parenthesis for {current_token_value}() function", self.line)
                    next_token_type, next_token_value = self.peek(2)[0], self.peek(2)[1]
                    if next_token_type != "IDENTIFIER":
                        self.error(f"invalid argument '{next_token_value}' for {current_token_value}() function", self.line)
                    variable_name = next_token_value
                    self.variables[variable_name]["mutable"] = True if current_token_value == "mut" else False
                elif current_token_value == "input":
                    next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                    if next_token_type != "PARENTHESIS" and next_token_value != "(":
                        self.error(f"missing opening parenthesis for input() function", self.line)
                    next_token_type, next_token_value = self.peek(2)[0], self.peek(2)[1]
                    input_prompt = ""
                    if next_token_type != "IDENTIFIER":
                        input_prompt = next_token_value
                    else:
                        input_prompt = self.variables[next_token_value]["value"]
                    next_token_type, next_token_value = self.peek(3)[0], self.peek(3)[1]
                    if next_token_type == "PARENTHESIS" and next_token_value == ")":
                        input(input_prompt)
                        self.advance()
                        continue
                    else:
                        if next_token_type != "IDENTIFIER":
                            self.error(f"can't assign input value to '{next_token_value}', output must go into a variable", self.line)
                        if not self.variables[next_token_value]["mutable"]:
                            self.error(f"can't assign input value to immutable variable {next_token_value}", self.line)
                        variable_name = next_token_value
                        next_token_type, next_token_value = self.peek(4)[0], self.peek(4)[1]
                        if next_token_type != "PARENTHESIS" and next_token_value != ")":
                            self.error(f"missing closing parenthesis for input() function", self.line)
                        self.variables[variable_name]["value"] = input(input_prompt)
                elif current_token_value == "clear":
                    next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                    if next_token_type != "PARENTHESIS" and next_token_value != "(":
                        self.error(f"missing opening parenthesis for clear() function", self.line)
                    next_token_type, next_token_value = self.peek(2)[0], self.peek(2)[1]
                    if next_token_type != "PARENTHESIS" and next_token_value != ")":
                        self.error(f"missing closing parenthesis for clear() function", self.line)
                    os.system('cls' if os.name == 'nt' else 'clear')
                elif current_token_value == "wait":
                    next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                    if next_token_type != "PARENTHESIS" and next_token_value != "(":
                        self.error(f"missing opening parenthesis for wait() function", self.line)
                    next_token_type, next_token_value = self.peek(2)[0], self.peek(2)[1]
                    if next_token_type == "PARENTHESIS" and next_token_value == ")":
                        pass
                    elif next_token_type == "IDENTIFIER":
                        variable_name = next_token_value
                        variable_value = self.variables[variable_name]["value"]
                        if type(variable_value) != int:
                            self.error(f"invalid waiting time '{variable_value}' for wait function (expects an integer of milliseconds)", self.line)
                        time.sleep(variable_value / 1000)
                    elif next_token_type == "NUMBER":
                        time.sleep(next_token_value / 1000)
                    else:
                        self.error(f"missing closing parenthesis for wait() function", self.line)
                elif current_token_value == "exit":
                    next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                    if next_token_type != "PARENTHESIS" and next_token_value != "(":
                        self.error(f"missing opening parenthesis for exit() function", self.line)
                    next_token_type, next_token_value = self.peek(2)[0], self.peek(2)[1]
                    if next_token_type == "PARENTHESIS" and next_token_value == ")":
                        sys.exit(0)
                    elif next_token_type == "IDENTIFIER":
                        variable_name = next_token_value
                        variable_value = self.variables[variable_name]["value"]
                        if type(variable_value) != int:
                            self.error(f"invalid error code '{variable_value}' for exit() function (expects an integer)", self.line)
                        sys.exit(variable_value)
                    elif next_token_type == "NUMBER":
                        sys.exit(next_token_value)
                    else:
                        self.error(f"missing closing parenthesis for exit() function", self.line)
                elif current_token_value == "if":
                    self.advance()
                    condition = self.peek_until(("CURLY", "{"))
                    self.curly_count += 1
                    truth = self.parse_condition(condition)
                    if not self.if_statement_truth_table.get(self.curly_count):
                        self.if_statement_truth_table[self.curly_count] = [truth]
                    else:
                        self.if_statement_truth_table[self.curly_count].append(truth)
                    if not truth:
                        self.skip_block()
                        continue
                elif current_token_value == "elseif":
                    self.advance()
                    previous_truths = self.if_statement_truth_table[self.curly_count + 1]
                    condition = self.peek_until(("CURLY", "{"))
                    self.curly_count += 1
                    truth = True
                    if True in previous_truths:
                        truth = False
                    if truth:
                        truth = self.parse_condition(condition)
                    self.if_statement_truth_table[self.curly_count].append(truth)
                    if not truth:
                        self.skip_block()
                        continue
                elif current_token_value == "else":
                    self.advance()
                    previous_truths = self.if_statement_truth_table[self.curly_count + 1]
                    condition = self.peek_until(("CURLY", "{"))
                    self.curly_count += 1
                    truth = True
                    if True in previous_truths:
                        truth = False
                    del self.if_statement_truth_table[self.curly_count]
                    if not truth:
                        self.skip_block()
                        continue
                elif current_token_value == "fn":
                    self.advance()
                    name_type = self.current_token[0]
                    name_value = self.current_token[1]
                    if name_type != "IDENTIFIER":
                        self.error(f"invalid function name '{name_value}'", self.line)
                    self.advance()
                    next_token = self.current_token
                    params = []
                    if next_token == ("CURLY", "{"):
                        self.skip_block_function(name_value, params, self.line)
                    elif next_token == ("SQUARE", "[") or next_token == ("PARENTHESIS", "("):
                        self.advance()
                        if next_token == ("SQUARE", "["):
                            oldparams = self.peek_until(("SQUARE", "]"))
                        elif next_token == ("PARENTHESIS", "("):
                            oldparams = self.peek_until(("PARENTHESIS", ")"))
                        for token in oldparams:
                            if token[0] != "IDENTIFIER":
                                self.error(f"invalid parameter name '{token[1]}' for function '{name_value}'", self.line)
                            params.append(token[1])
                        self.advance()
                        next_token = self.current_token
                        if next_token == ("CURLY", "{"):
                            self.skip_block_function(name_value, params, self.line)
                        else:
                            self.error("missing opening curly brace for function", self.line)
                elif current_token_value == "call":
                    function_type, function_value = self.peek()[0], self.peek()[1]
                    if function_type != "IDENTIFIER":
                        self.error(f"invalid function '{function_value}' being called", self.line)
                    function = self.functions[function_value]
                    next_token = self.peek(2)
                    variables = {}
                    if next_token != None:
                        if next_token[0] == "SQUARE" or next_token[0] == "PARENTHESIS":
                            self.advance()
                            self.advance()
                            self.advance()
                            if next_token[0] == "SQUARE":
                                parameters = self.peek_until(("SQUARE", "]"))
                            elif next_token[0] == "PARENTHESIS":
                                parameters = self.peek_until(("PARENTHESIS", ")")) 
                            idx = 0
                            for param in parameters:
                                if param[0] != "IDENTIFIER":
                                    variables[function["params"][idx]] = {
                                        "value": param[1],
                                        "mutable": True
                                    }
                                else:
                                    variables[function["params"][idx]] = {
                                        "value": self.variables[param[1]]["value"],
                                        "mutable": True
                                    }
                                idx += 1
                    new_interpreter = Interpreter(function["tokens"])
                    returned = new_interpreter.interpret(variables=variables, in_function=True, functions=self.functions)
                    next_token = self.peek()
                    if next_token is not None:
                        if next_token[0] == "RETURN_OPERATOR":
                            variable = self.peek(2)
                            type_ = variable[0]
                            value = variable[1]
                            if type_ != "IDENTIFIER":
                                self.error(f"invalid variable '{value}' getting passed as return variable in function call", self.line)
                            self.variables[value]["value"] = returned
                elif current_token_value == "return":
                    to_return = self.peek()
                    type_ = to_return[0]
                    value = to_return[1]
                    if not in_function:
                        self.error("can't use return keyword outside of a function", self.line)
                    if type_ != "IDENTIFIER":
                        self.return_value = value
                    else:
                        self.return_value = self.variables[value]["value"]
                elif current_token_value == "repeat":
                    repeat_type, repeat_value = self.peek()
                    self.advance()
                    self.advance()
                    if repeat_type == "IDENTIFIER":
                        repeat_value = self.variables[repeat_value]["value"]
                    self.skip_block_repeat(repeat_value)
                elif current_token_value == "foreach":
                    condition = [self.peek(), self.peek(2), self.peek(3)]
                    self.skip_block_foreach(condition)
                elif current_token_value == "while":
                    condition = self.peek_until(("CURLY", "{"))
                    self.skip_block_while(condition)
                elif current_token_value == "file":
                    next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                    self.advance()
                    if next_token_type != "KEYWORD":
                        self.error("what... what the fuck are you doing... with file I/O...? im scared...", self.line)
                    type_ = next_token_value
                    next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                    self.advance()
                    if next_token_type != "PARENTHESIS" and next_token_type != "(":
                        self.error("missing opening parenthesis for file function", self.line)
                    next_token_type, next_token_value = self.peek(3)[0], self.peek(3)[1]
                    if next_token_type != "PARENTHESIS" and next_token_type != ")":
                        self.error("missing closing parenthesis for file function", self.line)
                    next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                    self.advance()
                    if next_token_type == "IDENTIFIER":
                        next_token_value = self.variables[next_token_value]["value"]
                    file = next_token_value
                    file = os.path.join(parent_folder, os.path.basename(file))
                    if type_ == "write":
                        next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                        self.advance()
                        if next_token_type == "IDENTIFIER":
                            next_token_value = self.variables[next_token_value]["value"]
                        text_to_write = str(next_token_value).replace("\\n", "\n").replace("\\t", "\t").replace("\\b", "\b")
                        with open(file, 'w') as f:
                            f.write(text_to_write)
                    elif type_ == "read":
                        next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                        self.advance()
                        variable_output = next_token_value
                        with open(file, 'r') as f:
                            variable = self.variables[variable_output]
                            if not variable["mutable"]:
                                self.error(f"cannot change value of immutable variable '{variable_output}'", self.line)
                            variable["value"] = f.read()
                    elif type_ == "append":
                        next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                        self.advance()
                        if next_token_type == "IDENTIFIER":
                            next_token_value = self.variables[next_token_value]["value"]
                        text_to_write = next_token_value.replace("\\n", "\n").replace("\\t", "\t").replace("\\b", "\b")
                        with open(file, 'a') as f:
                            f.write(text_to_write)
                elif current_token_value == "system":
                    next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                    self.advance()
                    if next_token_type != "PARENTHESIS" and next_token_value != "(":
                        self.error("missing opening parenthesis for system() function", self.line)
                    next_token_type, next_token_value = self.peek(2)[0], self.peek(2)[1]
                    if next_token_type != "PARENTHESIS" and next_token_value != ")":
                        self.error("missing closing parenthesis for system() function", self.line)
                    next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                    self.advance()
                    if next_token_type == "IDENTIFIER":
                        next_token_value = self.variables[next_token_value]["value"]
                    command = next_token_value
                    cd_command = os.path.dirname(os.path.abspath(argv[1]))
                    subprocess.run(f"cd {cd_command} && {command}", shell=True, capture_output=False)
                elif current_token_value == "string":
                    self.advance()
                    next_value = self.current_token[1]
                    if next_value in ("upper", "lower", "trim"):
                        next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                        self.advance()
                        if next_token_type != "PARENTHESIS" and next_token_value != "(":
                            self.error("missing opening parenthesis for string function", self.line)
                        next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                        self.advance()
                        if next_token_type != "IDENTIFIER":
                            self.error("expected variable to convert to an upper string", self.line)
                        string = self.variables[next_token_value]
                        if not string["mutable"]:
                            self.error(f"cannot change value of immutable variable '{next_token_value}'", self.line)
                        next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                        self.advance()
                        if next_token_type != "PARENTHESIS" and next_token_value != ")":
                            self.error("missing closing parenthesis for string function", self.line)
                        if type(string["value"]) != str:
                            self.error("why are you trying to use string functions on a totally different type", self.line)
                        if next_value == "upper":
                            string["value"] = string["value"].upper()
                        elif next_value == "lower":
                            string["value"] = string["value"].lower()
                        elif next_value == "trim":
                            string["value"] = string["value"].strip()
                    elif next_value in ("replace"):
                        next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                        self.advance()
                        if next_token_type != "PARENTHESIS" and next_token_value != "(":
                            self.error("missing opening parenthesis for string function", self.line)
                        next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                        self.advance()
                        if next_token_type != "IDENTIFIER":
                            self.error("expected variable to convert to an upper string", self.line)
                        string = self.variables[next_token_value]
                        if not string["mutable"]:
                            self.error(f"cannot change value of immutable variable '{next_token_value}'", self.line)
                        if type(string["value"]) != str:
                            self.error("why are you trying to use string functions on a totally different type", self.line)
                        next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                        self.advance()
                        if next_token_type == "IDENTIFIER":
                            next_token_value = self.variables[next_token_value]["value"]
                        a = next_token_value.replace("\\n", "\n").replace("\\t", "\t").replace("\\\"", "\"")
                        if type(next_token_value) != str:
                            self.error("cannot use non-string value for string function", self.line)
                        next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                        self.advance()
                        if next_token_type == "IDENTIFIER":
                            next_token_value = self.variables[next_token_value]["value"]
                        b = next_token_value.replace("\\n", "\n").replace("\\t", "\t").replace("\\\"", "\"")
                        if type(next_token_value) != str:
                            self.error("cannot use non-string value for string function", self.line)
                        string["value"] = string["value"].replace(a, b)
                        next_token_type, next_token_value = self.peek()[0], self.peek()[1]
                        self.advance()
                        if next_token_type != "PARENTHESIS" and next_token_value != ")":
                            self.error("missing closing parenthesis for string function", self.line)
                    else:
                        self.error("what... what the fuck are you doing with string methods? i'm scared...", self.line)
                elif current_token_value == "list":
                    self.advance()
                    next_value = self.current_token[1]
                    if next_value in ("add", "remove", "get", "len", "pop", "set"):
                        type_ = next_value
                        self.advance()
                        next_token = self.current_token
                        if next_token != ("PARENTHESIS", "("):
                            self.error("missing opening parenthesis for list function", self.line)
                        self.advance()
                        next_token_type, next_token_value = self.current_token[0], self.current_token[1]
                        if next_token_type != "IDENTIFIER":
                            self.error("expected list variable as first argument to list function", self.line)
                        list_ = self.variables[next_token_value]
                        self.advance()
                        next_token_type, next_token_val = self.current_token[0], self.current_token[1]
                        if next_token_type == "IDENTIFIER":
                            next_token_val = self.variables[next_token_val]["value"]
                        if type_ == "add":
                            list_["value"].append(next_token_val)
                            next = self.peek()
                            if next != ("PARENTHESIS", ")"):
                                self.error("missing closing parenthesis for list function", self.line)
                        elif type_ == "len":
                            variable_name = self.current_token
                            if variable_name[0] != "IDENTIFIER":
                                self.error("expected variable to return list length to", self.line)
                            self.variables[variable_name[1]]["value"] = len(list_["value"])
                            next = self.peek()
                            if next != ("PARENTHESIS", ")"):
                                self.error("missing closing parenthesis for list function", self.line)
                        elif type_ == "remove":
                            next = self.peek()
                            if next != ("PARENTHESIS", ")"):
                                self.error("missing closing parenthesis for list function", self.line)
                            self.variables[next_token_value]["value"].pop(next_token_val)
                        elif type_ == "pop":
                            next = self.peek(2)
                            if next != ("PARENTHESIS", ")"):
                                self.error("missing closing parenthesis for list function", self.line)
                            index = next_token_val
                            variable = self.peek()
                            if variable[0] != "IDENTIFIER":
                                self.error("expected variable to return list value to", self.line)
                            self.variables[variable[1]]["value"] = self.variables[next_token_value]["value"].pop(index)
                        elif type_ == "get":
                            next = self.peek(2)
                            if next != ("PARENTHESIS", ")"):
                                self.error("missing closing parenthesis for list function", self.line)
                            index = next_token_val
                            variable = self.peek()
                            if variable[0] != "IDENTIFIER":
                                self.error("expected variable to return list value to", self.line)
                            if not self.variables[variable[1]]["mutable"]:
                                self.error(f"cannot change immutable value of variable '{variable[1]}'", self.line)
                            self.variables[variable[1]]["value"] = self.variables[next_token_value]["value"][index]
                        elif type_ == "set":
                            next = self.peek(2)
                            if next != ("PARENTHESIS", ")"):
                                self.error("missing closing parenthesis for list function", self.line)
                            index = next_token_val
                            variable = self.peek()
                            if variable[0] != "IDENTIFIER":
                                self.error("expected variable to return list value to", self.line)
                            if not self.variables[variable[1]]["mutable"]:
                                self.error(f"cannot change immutable value of variable '{variable[1]}'", self.line)
                            self.variables[next_token_value]["value"][index] = self.variables[variable[1]]["value"]
                elif current_token_value == "dict":
                    self.advance()
                    next = self.current_token
                    command = next
                    if next[1] not in ("get", "set", "delete"):
                        self.error("what... what are you doing with dict functions..? i fear you... (a.k.a. invalid dict function)", self.line)
                    self.advance()
                    next = self.current_token
                    if next != ("PARENTHESIS", "("):
                        self.error("missing opening parenthesis for dict function", self.line)
                    self.advance()
                    next = self.current_token
                    if next[0] != "IDENTIFIER":
                        self.error("expected variable (dictionary) as first argument to dict function", self.line)
                    dict_name = next[1]
                    #dict_ = self.variables[next[1]]["value"]
                    self.advance()
                    next = self.current_token
                    if next == "IDENTIFIER":
                        next = self.variables[next[1]]["value"]
                    else:
                        next = next[1]
                    key = next
                    if command[1] == "delete":
                        self.variables[dict_name]["value"].pop(key)
                        continue
                    self.advance()
                    next = self.current_token
                    if command[1] == "get":
                        if next[0] != "IDENTIFIER":
                            self.error("expected variable to return dict get() function value to", self.line)
                        self.variables[next[1]]["value"] = self.variables[dict_name]["value"][key]
                    elif command[1] == "set":
                        if next[0] == "IDENTIFIER":
                            self.variables[dict_name]["value"][key] = self.variables[next[1]]["value"]
                        else:
                            self.variables[dict_name]["value"][key] = next[1]
                    self.position -= 1
                elif current_token_value in ("ascii_char", "char_ascii"):
                    next = self.peek()
                    if next != ("PARENTHESIS", "("):
                        self.error("missing opening parenthesis for ascii function", self.line)
                    next = self.peek(3)
                    if next != ("PARENTHESIS", ")"):
                        self.error("missing closing parenthesis for ascii function", self.line)
                    value = self.peek(2)
                    if value[0] != "IDENTIFIER":
                        self.error("invalid argument passed to ascii function", self.line)
                    if current_token_value == "ascii_char":
                        self.variables[value[1]]["value"] = chr(self.variables[value[1]]["value"])
                    elif current_token_value == "char_ascii":
                        self.variables[value[1]]["value"] = ord(self.variables[value[1]]["value"])
                elif current_token_value in ("int", "float", "str"):
                    next = self.peek()
                    if next != ("PARENTHESIS", "("):
                        self.error("missing opening parenthesis for type conversion function", self.line)
                    next = self.peek(3)
                    if next != ("PARENTHESIS", ")"):
                        self.error("missing closing parenthesis for type conversion function", self.line)
                    next = self.peek(2)
                    next_type, next_value = next[0], next[1]
                    if next_type != "IDENTIFIER":
                        self.error("expected variable to convert value of", self.line)
                    if not self.variables[next_value]["mutable"]:
                        self.error(f"cannot change value of immutable variable '{next_value}'", self.line)
                    if current_token_value == "int":
                        self.variables[next_value]["value"] = int(self.variables[next_value]["value"])
                    elif current_token_value == "float":
                        self.variables[next_value]["value"] = float(self.variables[next_value]["value"])
                    if current_token_value == "str":
                        self.variables[next_value]["value"] = str(self.variables[next_value]["value"])
                elif current_token_value == "random":
                    next = self.peek()
                    if next != ("PARENTHESIS", "("):
                        self.error("missing opening parenthesis for random() function", self.line)
                    values = []
                    next = self.peek(5)
                    if next != ("PARENTHESIS", ")"):
                        self.error("missing closing parenthesis for random() function", self.line)
                    next = self.peek(2)
                    if next[0] != "IDENTIFIER":
                        self.error("expected variable to return random value to", self.line)
                    values.append(next[1])
                    next = self.peek(3)
                    if next[0] == "IDENTIFIER":
                        next = self.variables[next[1]]["value"]
                    else:
                        next = next[1]
                    values.append(next)
                    next = self.peek(4)
                    if next[0] == "IDENTIFIER":
                        next = self.variables[next[1]]["value"]
                    else:
                        next = next[1]
                    values.append(next)
                    if not self.variables[values[0]]["mutable"]:
                        self.error(f"cannot change immutable value of variable {value[0]}", self.line)
                    self.variables[values[0]]["value"] = random.randint(values[1], values[2])
                elif current_token_value == "import":
                    file = self.peek()
                    if file[0] == "IDENTIFIER":
                        file = self.variables[file]["value"]
                    elif file[0] == "STRING":
                        file = file[1]
                    else:
                        self.error(f"invalid argument '{file[1]}' passed to import", self.line)
                    with open(parent_folder + "\\" + file, 'r') as f:
                        lexer = Lexer(f.read(), keywords=keywords)
                        tokens = lexer.tokenize()
                        interpreter = Interpreter(tokens)
                        vars, funcs, classes, class_vars = interpreter.interpret(importing=True)
                        self.variables |= vars
                        self.functions |= funcs
                        self.classes |= classes
                        self.class_vars |= class_vars
                elif current_token_value == "split":
                    next = self.peek()
                    if next != ("PARENTHESIS", "("):
                        self.error("missing opening parenthesis for split() function", self.line)
                    self.advance()
                    next = self.peek()
                    if next[0] != "IDENTIFIER":
                        self.error("invalid argument passed to split() function", self.line)
                    else:
                        next = next[1]
                    variable = self.variables[next]["value"]
                    to_split = self.peek(2)
                    if to_split[0] == "IDENTIFIER":
                        to_split = self.variables[to_split[1]]["value"]
                    else:
                        to_split = to_split[1]
                    if to_split == "":
                        splitted = variable.split()
                    else:
                        splitted = variable.split(to_split)
                    self.variables[next]["value"] = splitted
                elif current_token_value in ("alpha", "digit", "alnum"):
                    command = current_token_value
                    self.advance()
                    next = self.current_token
                    if next != ("PARENTHESIS", "("):
                        self.error("missing opening parenthesis for alpha()/digit()/alnum() function")
                    self.advance()
                    val1 = self.current_token
                    if val1[0] == "IDENTIFIER":
                        val1 = self.variables[val1[1]]["value"]
                    else:
                        val1 = val1[1]
                    self.advance()
                    val2 = self.current_token
                    if val2[0] != "IDENTIFIER":
                        self.error("expected variable as 2nd argument to alpha()/digit()/alnum() function")
                    self.advance()
                    next = self.current_token
                    if next != ("PARENTHESIS", ")"):
                        self.error("missing closing parenthesis for alpha()/digit()/alnum() function")
                    if command == "alpha":
                        alpha = val1.isalpha()
                        self.variables[val2[1]]["value"] = 1 if alpha else 0
                    elif command == "digit":
                        digit = val1.isdigit()
                        self.variables[val2[1]]["value"] = 1 if digit else 0
                    elif command == "alnum":
                        alnum = val1.isalnum()
                        self.variables[val2[1]]["value"] = 1 if alnum else 0
                elif current_token_value in ("break", "continue"):
                    if current_token_value == "break":
                        self.broken = True
                    break
                elif current_token_value == "class":
                    name = self.peek()
                    if name[0] != "IDENTIFIER":
                        self.error(f"invalid class name '{name[1]}'", self.line)
                    self.advance()
                    self.advance()
                    parameters = []
                    if self.current_token == ("PARENTHESIS", "("):
                        self.advance()
                        pars = self.peek_until(("PARENTHESIS", ")"))
                        for p in pars:
                            if p[0] != "IDENTIFIER":
                                self.error(f"invalid class parameter name '{p[1]}'", self.line)
                            parameters.append(p[1])
                    self.skip_block_class(name[1], parameters, self.line)
                elif current_token_value == "self":
                    if cls==True:
                        self.advance()
                        if self.current_token == ("KEYWORD", "set"):
                            self.advance()
                            if self.current_token != ("PARENTHESIS", "("):
                                self.error("missing opening parenthesis for self set() function", self.line)
                            self.advance();self.advance();self.advance()
                            if self.current_token != ("PARENTHESIS", ")"):
                                self.error("missing closing parenthesis for self set() function", self.line)
                            self.position -= 3
                            self.advance()
                            ident = self.current_token
                            self.advance()
                            value = self.current_token
                            if ident[0] != "IDENTIFIER":
                                self.error("expected variable as first argument to self set() function", self.line)
                            if value[0] == "IDENTIFIER":
                                value = self.variables[value[1]]["value"]
                            classe["self"][ident[1]] = {
                                "value": value,
                                "mutable": False
                            }
                            self.variables[ident[1]] = {
                                "value": value,
                                "mutable": False
                            }
            elif current_token_type == "MODIFIER":
                if current_token_value == "class_variable":
                    next = self.peek()
                    if next != ("PARENTHESIS", "("):
                        self.error("missing opening parenthesis for @class() modifier", self.line)
                    next = self.peek(3)
                    if next != ("PARENTHESIS", ")"):
                        self.error("missing closing parenthesis for @class() modifier", self.line)
                    class_ = self.peek(2)
                    if class_[0] != "IDENTIFIER":
                        self.error("expected a class name as the argument for  @class() modifier", self.line)
                    self.advance();self.advance();self.advance();self.advance()
                    next = self.current_token
                    if next == ("KEYWORD", "call"):
                        self.advance()
                        function = self.current_token
                        if function[0] != "IDENTIFIER":
                            self.error("expected class method as call argument", self.line)
                        self.advance()
                        next = self.current_token
                        params = []
                        if next == ("PARENTHESIS", "("):
                            self.advance()
                            params = self.peek_until(("PARENTHESIS", ")"))
                        new_interp = Interpreter(self.class_variables[class_[1]]["methods"][function[1]])
                        return_value = new_interp.interpret(variables=self.class_variables[class_[1]]["self"], functions=self.class_variables[class_[1]]["methods"], cls=True, classe=class_, in_function=True)
                        if self.peek() == ("RETURN_OPERATOR", "->"):
                            variable_name = self.peek(2)
                            if variable_name[0] != "IDENTIFIER":
                                self.error("expected variable as return value for class_variable call function", self.line)
                            self.variables[variable_name[1]]["value"] = return_value
                elif current_token_value == "class":
                    next = self.peek()
                    if next != ("PARENTHESIS", "("):
                        self.error("missing opening parenthesis for @class() modifier", self.line)
                    next = self.peek(3)
                    if next != ("PARENTHESIS", ")"):
                        self.error("missing closing parenthesis for @class() modifier", self.line)
                    class_ = self.peek(2)
                    if class_[0] != "IDENTIFIER":
                        self.error("expected a class name as the argument for  @class() modifier", self.line)
                    self.advance();self.advance();self.advance();self.advance()
                    next = self.current_token
                    if next == ("KEYWORD", "new"):
                        self.advance()
                        next = self.current_token
                        if next != ("PARENTHESIS", "("):
                            self.error("missing opening parenthesis for class new() function", self.line)
                        self.advance()
                        args = self.peek_until(("PARENTHESIS", ")"))
                        idx = 0
                        for arg in args:
                            args[idx] = arg[1]
                            idx += 1
                        _class_ = self.classes[class_[1]]
                        new_interp = Interpreter(_class_["methods"]["init"])
                        parameter_list = {}
                        idx = 0
                        for param in _class_["params"]:
                            parameter_list[param] = {
                                "value": args[idx],
                                "mutable": True
                            }
                            idx += 1
                        new_interp.interpret(variables=_class_["self"] | parameter_list, cls=True, classe=_class_)
                        if self.peek() == ("RETURN_OPERATOR", "->"):
                            next = self.peek(2)
                            self.advance();self.advance()
                            if next[0] != "IDENTIFIER":
                                self.error("expected variable name as class variable name", self.line)
                            self.class_variables[next[1]] = _class_
                        _class_["methods"].pop('init')
            elif current_token_type == "CREMENTATION":
                left = self.peek(-1)
                if left[0] == 'IDENTIFIER':
                    variable_name = left[1]
                    if not self.variables[variable_name]["mutable"]:
                        self.error(f"cannot change value of immutable variable {variable_name}", self.line)
                    if current_token_value == "++":
                        self.variables[variable_name]["value"] += 1
                    elif current_token_value == "--":
                        self.variables[variable_name]["value"] -= 1
                else:
                    self.error("cannot increment/decrement something that is not a variable", self.line)
            elif current_token_type == "ARITHMETIC_ASSIGNMENT":
                left_type, left_value = self.peek(-1)[0], self.peek(-1)[1]
                if left_type != "IDENTIFIER":
                    self.error(f"invalid assignment left side '{left_value}'", self.line)
                else:
                    right_type, right_value = self.peek()[0], self.peek()[1]
                    if not self.variables[left_value]["mutable"]:
                        self.error(f"can't change immutable variable {left_value}'s value", self.line)
                    if right_type != "IDENTIFIER":
                        value = right_value
                    else:
                        value = self.variables[right_value]["value"]
                    if current_token_value == "+=":
                        self.variables[left_value]["value"] += value
                    elif current_token_value == "-=":
                        self.variables[left_value]["value"] -= value
                    elif current_token_value == "*=":
                        self.variables[left_value]["value"] *= value
                    elif current_token_value == "/=":
                        self.variables[left_value]["value"] /= value
                    elif current_token_value == "//=":
                        self.variables[left_value]["value"] //= value
                    elif current_token_value == "%=":
                        self.variables[left_value]["value"] %= value
                    elif current_token_value == "^=":
                        self.variables[left_value]["value"] **= value
            elif current_token_type == "ASSIGNMENT":
                left_type, left_value = self.peek(-1)[0], self.peek(-1)[1]
                if left_type != "IDENTIFIER":
                    self.error(f"invalid assignment left side '{left_value}'", self.line)
                else:
                    right_type, right_value = self.peek()[0], self.peek()[1]
                    if not self.variables[left_value]["mutable"]:
                        self.error(f"can't change immutable variable {left_value}'s value", self.line)
                    if right_type != "IDENTIFIER":
                        self.variables[left_value]["value"] = right_value
                    else:
                        value = self.variables[right_value]["value"]
                        self.variables[left_value]["value"] = value
            self.advance()
        if importing:
            return self.variables, self.functions, self.classes, self.class_variables
        return self.return_value

VERSION_INFO = rf"""{colorama.Fore.CYAN}
 /$$$$$$$                                /$$   /$$    
| $$__  $$                              | $$  | $$    
| $$  \ $$  /$$$$$$   /$$$$$$$  /$$$$$$ | $$ /$$$$$$  
| $$$$$$$  |____  $$ /$$_____/ |____  $$| $$|_  $$_/  
| $$__  $$  /$$$$$$$|  $$$$$$   /$$$$$$$| $$  | $$    
| $$  \ $$ /$$__  $$ \____  $$ /$$__  $$| $$  | $$ /$$
| $$$$$$$/|  $$$$$$$ /$$$$$$$/|  $$$$$$$| $$  |  $$$$/
|_______/  \_______/|_______/  \_______/|__/   \___/  
{colorama.Fore.RESET}
Basalt Language v1.1.0
Build: 2026-01-27
"""

HELP_TEXT = """Basalt Interpreter - Usage: basalt [-flag/--flag] [file.basalt]

Flags:
  -v, --version     Show version info
  -h, --help        Show this help menu
  -i, --info        Show engine stats (kind of a flex)
  -r, --run         Run a .basalt file
  -re, --repl       Run the Basalt REPL (BETA)

Basalt Syntax:
  fn name() { }                         Define a function
  let [var] = [val]                     Declare an immutable variable
  let mut [var] = [val]                 Declare a mutable variable
  let undef [var]                       Declare a null variable (mutable)
  print("text"), println("text")        String/Number printing
  printf("[var]")                       Formatted string printing
  list [op]([args])                     List operations (get, add, remove, len, pop)
  dict [op]([args])                     Dict operations (get, set, delete)
  file [op]([args])                     File operations (read, write, append)
  [loop] [condition] { }                Start a loop (repeat, while, foreach)
Good To Know:
  [] vs ()          You can use both [] and () when defining or calling a user-defined function,
                    but you can only use () when calling a pre-defined function (e.g. print()).
  Mutable?          Only 'mut' and 'undef' variables are mutable (let [mut/undef] [var] = [val]).
                    Variables with only 'let' before their names are immutable.
  mut()/immut()     The mut() keyword makes a variable mutable, while immut() makes a variable 
                    immutable. Use when you can't figure out why your variable is immutable.
  Interpolation     printf("Val: [x]") only works with [brackets], not {braces}.
  Case-Sensitivity  Basalt is case sensitive, e.g. 'Let' is not the same as 'let'.
These won't be enough however. You'll need to learn other Basalt concepts on your own."""

INFO_TEXT = """Basalt Engine Information:
  Version: 1.1.0
  Build: 2026-01-17
  Interpreter written in: Python
  Memory usage: probably a lot considering it's Python and this language is unoptimized
  Interpreter size: probably around 60-100kb (maybe more)
  Developed by: BasaltDev (i'm not leaking my name bro)
  Developed in: ~3-4 days"""

def main():
    global argv
    global argc
    if argc < 2:
        print(VERSION_INFO)
        print("Usage: basalt [-flag/--flag] [file.basalt]")
        return
    
    argv = argv[1:]

    if argc > 1:
        flag = sys.argv[1]

        if flag in ["-v", "--version"]:
            print(VERSION_INFO)
            return
        elif flag in ["-h", "--help"]:
            print(HELP_TEXT)
            return
        elif flag in ["-i", "--info"]:
            print(INFO_TEXT)
            return
        elif flag in ["-r", "--run"]:
            argv = argv[1:]
            if len(argv) < 1:
                print("Error: -r/--run flag requires a file name")
                return
            global parent_folder
            parent_folder = os.path.dirname(os.path.abspath(argv[0]))
            if not os.path.exists(os.path.join(parent_folder, os.path.basename(argv[0]))):
                print("Error: Expected an actually existing file to run")
                return
            code = open(argv[0], 'r').read()
            lexer = Lexer(code, keywords=keywords)
            tokens = lexer.tokenize()
            interpreter = Interpreter(tokens)
            interpreter.interpret()
            #print(interpreter.class_variables)
        elif flag in ["-re", "--repl"]:
            print(VERSION_INFO[:-1])
            print("Basalt REPL (Build 2026-01-27)")
            try:
                variables, functions = {}, {}
                while 1 == 1:
                    command = input("> ")
                    lexer = Lexer(command, keywords=keywords)
                    tokens = lexer.tokenize()
                    interpreter = Interpreter(tokens, repl=True)
                    try:
                        variables, functions = interpreter.interpret(variables=variables, functions=functions, importing=True)
                    except:
                        pass
                    print()
            except:
                sys.exit()
        else:
            print(VERSION_INFO)
            print("Usage: basalt [-flag/--flag] [file.basalt]")
            return
if __name__ == "__main__":
    main()
