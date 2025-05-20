from dataclasses import dataclass
from lexer import Token

# AST Node Definitions
@dataclass
class NumberLiteral:
    value: float

@dataclass
class StringLiteral:
    value: str

@dataclass
class Identifier:
    name: str

@dataclass
class BinaryOp:
    left: any
    op: str
    right: any

@dataclass
class VariableDeclaration:
    kind: str  # 'let' | 'const' | 'var'
    name: str
    value: any

@dataclass
class PrintStatement:
    value: list[any]

@dataclass
class FunctionDeclaration:
    name: str
    params: list[str]
    body: list[any]

@dataclass
class CallExpression:
    callee: any
    arguments: list[any]

@dataclass
class ReturnStatement:
    argument: any

@dataclass
class IfStatement:
    test: any
    consequent: list[any]
    alternate: list[any] | None = None

@dataclass
class WhileStatement:
    test: any
    body: list[any]

@dataclass
class Assignment:
    left: Identifier
    right: any


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def match(self, *types):
        token = self.current()
        if token and token.type in types:
            self.pos += 1
            return token
        return None

    def expect(self, type_, value=None):
        token = self.match(type_)
        if not token or (value and token.value != value):
            raise SyntaxError(f"Expected token {type_} {value}, got {self.current()}")
        return token

    def skip_newlines(self):
        while self.current() and self.current().type == 'NEWLINE':
            self.pos += 1

    def parse(self):
        statements = []
        while self.current():
            self.skip_newlines()
            if self.current() and self.current().type == 'PUNCT' and self.current().value == '}':
                break  # stop parsing when block ends
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements

    def parse_statement(self):
        self.skip_newlines()
        tok = self.current()

        if not tok:
            return None

        if tok.type == 'PUNCT' and tok.value == '}':
            return None  # Allow early block closure

        if tok.type == 'ID' and tok.value in ('let', 'const', 'var'):
            self.match('ID')
            stmt = self.parse_variable_declaration()
            self.expect('PUNCT', ';')
            return stmt

        elif tok.type == 'ID' and tok.value == 'function':
            self.match('ID')
            return self.parse_function_declaration()

        elif tok.type == 'ID' and tok.value == 'return':
            stmt = self.parse_return_statement()
            self.expect('PUNCT', ';')
            return stmt

        elif tok.type == 'ID' and tok.value == 'if':
            return self.parse_if_statement()

        elif tok.type == 'ID' and tok.value == 'while':
            return self.parse_while_statement()

        elif tok.type == 'ID' and tok.value == 'console':
            return self.parse_console_log()

        else:
            expr = self.parse_expression()
            self.expect('PUNCT', ';')
            return expr

    def parse_variable_declaration(self):
        kind_token = self.tokens[self.pos - 1]  # last matched 'let'/'const'/'var'
        name_token = self.expect('ID')
        self.expect('OP', '=')  # Expect '=' operator
        expr = self.parse_expression()
        # semicolon is expected by caller
        return VariableDeclaration(kind=kind_token.value, name=name_token.value, value=expr)

    def parse_function_declaration(self):
        name_token = self.expect('ID')
        self.expect('PUNCT', '(')
        params = []
        while True:
            tok = self.current()
            if not tok:
                raise SyntaxError("Unexpected end of input in function parameters")
            if tok.type == 'PUNCT' and tok.value == ')':
                self.pos += 1
                break
            elif tok.type == 'ID':
                params.append(tok.value)
                self.pos += 1
                if self.current() and self.current().type == 'PUNCT' and self.current().value == ',':
                    self.pos += 1  # consume comma
            else:
                raise SyntaxError("Invalid function parameter list")

        self.expect('PUNCT', '{')
        body = []
        self.skip_newlines()
        while self.current() and not (self.current().type == 'PUNCT' and self.current().value == '}'):
            self.skip_newlines()
            if self.current() and self.current().type == 'PUNCT' and self.current().value == '}':
                break
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
            self.skip_newlines()
        self.expect('PUNCT', '}')
        return FunctionDeclaration(name=name_token.value, params=params, body=body)

    def parse_return_statement(self):
        self.expect('ID', 'return')
        expr = self.parse_expression()
        # semicolon expected by caller
        return ReturnStatement(argument=expr)

    def parse_if_statement(self):
        self.expect('ID', 'if')
        self.expect('PUNCT', '(')
        test = self.parse_expression()
        self.expect('PUNCT', ')')
        self.expect('PUNCT', '{')
        consequent = []
        while self.current() and not (self.current().type == 'PUNCT' and self.current().value == '}'):
            stmt = self.parse_statement()
            if stmt is not None:
                consequent.append(stmt)
        self.expect('PUNCT', '}')

        alternate = None
        if self.current() and self.current().type == 'ID' and self.current().value == 'else':
            self.expect('ID', 'else')
            self.expect('PUNCT', '{')
            alternate = []
            while self.current() and not (self.current().type == 'PUNCT' and self.current().value == '}'):
                stmt = self.parse_statement()
                if stmt is not None:
                    alternate.append(stmt)
            self.expect('PUNCT', '}')

        return IfStatement(test=test, consequent=consequent, alternate=alternate)

    def parse_while_statement(self):
        self.expect('ID', 'while')
        self.expect('PUNCT', '(')
        test = self.parse_expression()
        self.expect('PUNCT', ')')
        self.expect('PUNCT', '{')
        body = []
        while self.current() and not (self.current().type == 'PUNCT' and self.current().value == '}'):
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
        self.expect('PUNCT', '}')
        return WhileStatement(test=test, body=body)

    def parse_console_log(self):
        self.expect('ID', 'console')
        self.expect('DOT')
        log_id = self.expect('ID')
        if log_id.value != 'log':
            raise SyntaxError("Expected 'log' after 'console.'")
        self.expect('PUNCT', '(')
        args = []
        if self.current() and not (self.current().type == 'PUNCT' and self.current().value == ')'):
            args.append(self.parse_expression())
            while self.current() and self.current().type == 'PUNCT' and self.current().value == ',':
                self.pos += 1  # consume ','
                args.append(self.parse_expression())
        self.expect('PUNCT', ')')
        self.expect('PUNCT', ';')
        return PrintStatement(value=args)

    def parse_expression(self):
        return self.parse_assignment()

    def parse_equality(self):
        node = self.parse_comparison()
        while self.current() and self.current().type == 'OP' and self.current().value in ('==', '!='):
            op = self.match('OP').value
            right = self.parse_comparison()
            node = BinaryOp(left=node, op=op, right=right)
        return node

    def parse_assignment(self):
        node = self.parse_equality()  # or parse_comparison() if you want

        if self.current() and self.current().type == 'OP' and self.current().value == '=':
            self.match('OP')  # consume '='
            right = self.parse_assignment()  # right-associative
            # For assignment, the left must be an Identifier (variable)
            if not isinstance(node, Identifier):
                raise SyntaxError("Invalid assignment target")
            # You can define an Assignment AST node or reuse VariableDeclaration for statements
            # But here just return a special BinaryOp for assignment, or better, define an Assignment node.
            return Assignment(left=node, right=right)

        return node

    def parse_comparison(self):
        node = self.parse_term()
        while self.current() and self.current().type == 'OP' and self.current().value in ('<', '>', '<=', '>='):
            op = self.match('OP').value
            right = self.parse_term()
            node = BinaryOp(left=node, op=op, right=right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current() and self.current().type == 'OP' and self.current().value in ('+', '-'):
            op = self.match('OP').value
            right = self.parse_factor()
            node = BinaryOp(left=node, op=op, right=right)
        return node

    def parse_factor(self):
        node = self.parse_atom()
        while self.current() and self.current().type == 'OP' and self.current().value in ('*', '/'):
            op = self.match('OP').value
            right = self.parse_atom()
            node = BinaryOp(left=node, op=op, right=right)
        return node

    def parse_atom(self):
        token = self.current()
        if not token:
            raise SyntaxError("Unexpected end of input")

        if token.type == 'NUMBER':
            self.pos += 1
            return NumberLiteral(value=float(token.value))

        elif token.type == 'STRING':
            self.pos += 1
            return StringLiteral(value=token.value)

        elif token.type == 'ID':
            self.pos += 1
            ident = Identifier(name=token.value)

            # Check for function call safely
            if self.current() and self.current().type == 'PUNCT' and self.current().value == '(':
                self.pos += 1  # consume '('
                args = []
                while self.current() and not (self.current().type == 'PUNCT' and self.current().value == ')'):
                    args.append(self.parse_expression())
                    if self.current() and self.current().type == 'PUNCT' and self.current().value == ',':
                        self.pos += 1
                self.expect('PUNCT', ')')
                return CallExpression(callee=ident, arguments=args)

            return ident

        elif token.type == 'PUNCT' and token.value == '(':
            self.pos += 1
            expr = self.parse_expression()
            self.expect('PUNCT', ')')
            return expr

        raise SyntaxError(f"Unexpected token: {token}")
