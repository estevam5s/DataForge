# 🚀 Guia Completo: Como Publicar uma Nova Linguagem de Programação

> **Um guia abrangente para criar, desenvolver e publicar uma linguagem de programação usando a arquitetura Python**

---

## 📋 Índice

1. [Visão Geral](#-visão-geral)
2. [Planejamento e Design](#-planejamento-e-design)
3. [Estrutura do Projeto](#-estrutura-do-projeto)
4. [Implementação Core](#-implementação-core)
5. [Empacotamento](#-empacotamento)
6. [Testes e Qualidade](#-testes-e-qualidade)
7. [Documentação](#-documentação)
8. [Publicação no PyPI](#-publicação-no-pypi)
9. [GitHub e Controle de Versão](#-github-e-controle-de-versão)
10. [CI/CD e Automação](#-cicd-e-automação)
11. [Marketing e Comunidade](#-marketing-e-comunidade)
12. [Manutenção e Evolução](#-manutenção-e-evolução)

---

## 🎯 Visão Geral

### O que é uma Linguagem de Programação Baseada em Python?

Uma linguagem interpretada que:
- **Usa Python como runtime**: Roda sobre o interpretador Python
- **Sintaxe própria**: Define sua própria sintaxe e palavras-chave
- **Transpilação/Interpretação**: Converte código fonte para Python ou executa diretamente
- **Ecossistema aproveitado**: Utiliza o vasto ecossistema de packages Python

### Exemplos de Sucesso
- **CoffeeScript** → JavaScript
- **TypeScript** → JavaScript  
- **Kotlin** → JVM/JavaScript
- **DataForge** → Python *(nosso exemplo)*

---

## 🧠 Planejamento e Design

### 1. Definição da Linguagem

#### Propósito e Nicho
```markdown
❓ Perguntas essenciais:
- Qual problema sua linguagem resolve?
- Quem é o público-alvo?
- O que a diferencia das existentes?
- Qual o domínio de aplicação? (web, data science, sistemas, etc.)
```

#### Filosofia da Linguagem
```markdown
Exemplo - DataForge:
✨ "Sintaxe natural e intuitiva"
🚀 "Performance sem complexidade" 
📊 "Data science simplificado"
🔧 "Produtividade maximizada"
```

### 2. Design de Sintaxe

#### Palavras-chave e Operadores
```python
# Exemplo de mapeamento DataForge → Python
KEYWORDS = {
    'out': 'print',           # output
    'in': 'input',           # input  
    'given': 'if',           # conditional
    'orif': 'elif',          # else if
    'otherwise': 'else',     # else
    'cycle': 'for',          # loops
    'persist': 'while',      # while loop
    'action': 'def',         # functions
    'yield': 'return',       # return
    'blueprint': 'class',    # classes
    'spawn': 'instantiate',  # object creation
}
```

#### Regras Gramaticais
```bnf
# Gramática BNF simplificada
program     ::= statement*
statement   ::= assignment | conditional | loop | function | expression
assignment  ::= IDENTIFIER ":=" expression
conditional ::= "given" expression ":" block ("orif" expression ":" block)* ("otherwise" ":" block)?
function    ::= "action" IDENTIFIER "(" params? ")" ":" block
```

---

## 🏗️ Estrutura do Projeto

### Organização de Diretórios

```
MinhaLinguagem/
├── 📄 README.md                    # Documentação principal  
├── 📄 LICENSE                      # Licença (MIT recomendada)
├── 📄 setup.py                     # Configuração de instalação
├── 📄 setup.cfg                    # Configurações adicionais
├── 📄 pyproject.toml              # Build system moderno
├── 📄 requirements.txt             # Dependências
├── 📄 requirements-dev.txt         # Dependências de desenvolvimento
├── 📄 MANIFEST.in                  # Arquivos para distribuição
├── 📄 .gitignore                   # Arquivos ignorados pelo Git
├── 📄 .github/                     # GitHub Actions e templates
│   ├── workflows/
│   │   ├── ci.yml                 # Continuous Integration
│   │   ├── publish.yml            # Publicação automática
│   │   └── docs.yml               # Deploy de documentação
│   ├── ISSUE_TEMPLATE/            # Templates de issues
│   └── PULL_REQUEST_TEMPLATE.md   # Template de PR
├── 📁 linguagem/                   # Código fonte principal
│   ├── 📄 __init__.py             # Inicialização do package
│   ├── 📄 __main__.py             # Entry point (python -m linguagem)
│   ├── 📄 cli.py                  # Interface de linha de comando
│   ├── 📄 lexer.py                # Análise léxica (tokenização)
│   ├── 📄 parser.py               # Análise sintática (AST)
│   ├── 📄 interpreter.py          # Interpretador/Transpilador
│   ├── 📄 ast_nodes.py            # Nós da AST
│   ├── 📄 tokens.py               # Definições de tokens
│   ├── 📄 environment.py          # Gerenciamento de escopo
│   ├── 📄 errors.py               # Tipos de erro customizados
│   ├── 📄 builtins.py             # Funções built-in
│   ├── 📄 repl.py                 # REPL interativo
│   └── 📁 stdlib/                 # Biblioteca padrão
│       ├── 📄 __init__.py
│       ├── 📄 math_lib.py         # Matemática
│       ├── 📄 io_lib.py           # I/O e arquivos
│       ├── 📄 web_lib.py          # HTTP e web
│       └── 📄 data_lib.py         # Estruturas de dados
├── 📁 examples/                    # Programas exemplo
│   ├── 📄 01_hello.ext            # Hello World
│   ├── 📄 02_variables.ext        # Variáveis
│   ├── 📄 03_functions.ext        # Funções
│   └── 📄 ...                     # Mais exemplos
├── 📁 tests/                       # Testes automatizados
│   ├── 📄 __init__.py
│   ├── 📄 test_lexer.py           # Testes do lexer  
│   ├── 📄 test_parser.py          # Testes do parser
│   ├── 📄 test_interpreter.py     # Testes do interpretador
│   └── 📄 test_examples.py        # Testes dos exemplos
├── 📁 docs/                        # Documentação
│   ├── 📄 index.md                # Página inicial
│   ├── 📄 tutorial.md             # Tutorial
│   ├── 📄 reference.md            # Referência da linguagem
│   └── 📄 api.md                  # API documentation
├── 📁 tools/                       # Ferramentas auxiliares
│   ├── 📄 benchmark.py            # Benchmarks
│   ├── 📄 syntax_highlighter.py   # Syntax highlighting
│   └── 📄 vscode_extension/       # Extensão VS Code
└── 📁 build/                       # Arquivos de build (ignorado)
```

### Arquivos de Configuração Essenciais

#### `setup.py` - Configuração Principal
```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="minha-linguagem",
    version="1.0.0",
    author="Seu Nome",
    author_email="seu@email.com",
    description="Uma linguagem de programação revolucionária",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/usuario/minha-linguagem",
    project_urls={
        "Bug Tracker": "https://github.com/usuario/minha-linguagem/issues",
        "Documentation": "https://minha-linguagem.readthedocs.io",
        "Source Code": "https://github.com/usuario/minha-linguagem",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Compilers",
    ],
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",      # CLI framework
        "colorama>=0.4.4",   # Cross-platform colored output
        "rich>=10.0.0",      # Rich text and beautiful formatting
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
            "pre-commit>=2.15",
        ],
        "docs": [
            "mkdocs>=1.2",
            "mkdocs-material>=7.0",
            "mkdocs-mermaid2-plugin>=0.5",
        ],
        "web": [
            "uvicorn>=0.15",
            "fastapi>=0.70",
        ],
    },
    entry_points={
        "console_scripts": [
            "minha-linguagem=linguagem.cli:main",
            "ml=linguagem.cli:main",  # Alias curto
        ],
    },
    include_package_data=True,
    package_data={
        "linguagem": [
            "stdlib/*.py",
            "templates/*.template",
        ],
    },
    zip_safe=False,
)
```

#### `pyproject.toml` - Build System Moderno
```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "minha-linguagem"
authors = [{name = "Seu Nome", email = "seu@email.com"}]
description = "Uma linguagem de programação revolucionária"
readme = "README.md"
requires-python = ">=3.10"
keywords = ["programming-language", "interpreter", "compiler"]
license = {text = "MIT"}
classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3",
]
dependencies = [
    "click>=8.0.0",
    "colorama>=0.4.4",
    "rich>=10.0.0",
]
dynamic = ["version"]

[project.urls]
Homepage = "https://github.com/usuario/minha-linguagem"
Documentation = "https://minha-linguagem.readthedocs.io"
Repository = "https://github.com/usuario/minha-linguagem.git"
"Bug Tracker" = "https://github.com/usuario/minha-linguagem/issues"

[project.scripts]
minha-linguagem = "linguagem.cli:main"
ml = "linguagem.cli:main"

[project.optional-dependencies]
dev = ["pytest>=6.0", "pytest-cov>=2.0", "black>=21.0", "flake8>=3.8"]
docs = ["mkdocs>=1.2", "mkdocs-material>=7.0"]

[tool.setuptools_scm]
write_to = "linguagem/_version.py"

[tool.black]
line-length = 88
target-version = ['py310']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=linguagem --cov-report=html --cov-report=term"

[tool.mypy]
python_version = "3.10"
strict = true
```

---

## ⚙️ Implementação Core

### 1. Lexer (Análise Léxica)

```python
# linguagem/tokens.py
from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional

class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    
    # Keywords
    IF = auto()          # given
    ELSE = auto()       # otherwise  
    WHILE = auto()      # persist
    FOR = auto()        # cycle
    FUNCTION = auto()   # action
    RETURN = auto()     # yield
    CLASS = auto()      # blueprint
    
    # Operators
    PLUS = auto()       # +
    MINUS = auto()      # -
    MULTIPLY = auto()   # *
    DIVIDE = auto()     # /
    ASSIGN = auto()     # :=
    EQUAL = auto()      # is
    
    # Delimiters
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    COLON = auto()      # :
    NEWLINE = auto()    # \n
    EOF = auto()        # End of file

@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int
    
# linguagem/lexer.py
import re
from typing import List, Iterator
from .tokens import Token, TokenType

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        
        # Mapeamento keywords
        self.keywords = {
            'given': TokenType.IF,
            'otherwise': TokenType.ELSE,
            'persist': TokenType.WHILE,
            'cycle': TokenType.FOR,
            'action': TokenType.FUNCTION,
            'yield': TokenType.RETURN,
            'blueprint': TokenType.CLASS,
        }
        
        # Padrões regex
        self.patterns = [
            (r'\d+(\.\d+)?', TokenType.NUMBER),
            (r'"[^"]*"', TokenType.STRING),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),
            (r':=', TokenType.ASSIGN),
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.MULTIPLY),
            (r'/', TokenType.DIVIDE),
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            (r'\{', TokenType.LBRACE),
            (r'\}', TokenType.RBRACE),
            (r':', TokenType.COLON),
            (r'\n', TokenType.NEWLINE),
            (r'\s+', None),  # Skip whitespace
            (r'#.*', None),  # Skip comments
        ]
    
    def tokenize(self) -> List[Token]:
        tokens = []
        
        while self.position < len(self.source):
            matched = False
            
            for pattern, token_type in self.patterns:
                regex = re.compile(pattern)
                match = regex.match(self.source, self.position)
                
                if match:
                    value = match.group(0)
                    
                    if token_type is not None:  # Skip whitespace and comments
                        # Check if it's a keyword
                        if token_type == TokenType.IDENTIFIER and value in self.keywords:
                            token_type = self.keywords[value]
                        
                        token = Token(token_type, value, self.line, self.column)
                        tokens.append(token)
                    
                    # Update position
                    self.position = match.end()
                    if value == '\n':
                        self.line += 1
                        self.column = 1
                    else:
                        self.column += len(value)
                    
                    matched = True
                    break
            
            if not matched:
                raise SyntaxError(f"Unexpected character '{self.source[self.position]}' at line {self.line}, column {self.column}")
        
        tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return tokens
```

### 2. AST (Abstract Syntax Tree)

```python
# linguagem/ast_nodes.py
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict
from dataclasses import dataclass

class ASTNode(ABC):
    """Base class for all AST nodes"""
    pass

class Expression(ASTNode):
    """Base class for expressions"""
    pass

class Statement(ASTNode):
    """Base class for statements"""
    pass

@dataclass
class NumberLiteral(Expression):
    value: float

@dataclass 
class StringLiteral(Expression):
    value: str

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class BinaryOperation(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class Assignment(Statement):
    name: str
    value: Expression

@dataclass
class IfStatement(Statement):
    condition: Expression
    then_block: List[Statement]
    else_block: Optional[List[Statement]] = None

@dataclass
class WhileLoop(Statement):
    condition: Expression
    body: List[Statement]

@dataclass
class FunctionDef(Statement):
    name: str
    parameters: List[str]
    body: List[Statement]

@dataclass
class FunctionCall(Expression):
    name: str
    arguments: List[Expression]

@dataclass
class ReturnStatement(Statement):
    value: Optional[Expression]

@dataclass
class Program(ASTNode):
    statements: List[Statement]
```

### 3. Parser (Análise Sintática)

```python
# linguagem/parser.py
from typing import List, Optional
from .tokens import Token, TokenType
from .ast_nodes import *
from .errors import ParseError

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0] if tokens else None
    
    def error(self, message: str):
        if self.current_token:
            raise ParseError(f"{message} at line {self.current_token.line}, column {self.current_token.column}")
        else:
            raise ParseError(message)
    
    def advance(self):
        if self.position < len(self.tokens) - 1:
            self.position += 1
            self.current_token = self.tokens[self.position]
        return self.current_token
    
    def match(self, *token_types: TokenType) -> bool:
        if self.current_token and self.current_token.type in token_types:
            return True
        return False
    
    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.match(token_type):
            token = self.current_token
            self.advance()
            return token
        else:
            self.error(message)
    
    def parse(self) -> Program:
        statements = []
        
        while not self.match(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                self.advance()
                continue
                
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        
        return Program(statements)
    
    def statement(self) -> Optional[Statement]:
        if self.match(TokenType.IDENTIFIER):
            return self.assignment_or_expression()
        elif self.match(TokenType.IF):
            return self.if_statement()
        elif self.match(TokenType.WHILE):
            return self.while_statement()
        elif self.match(TokenType.FUNCTION):
            return self.function_definition()
        elif self.match(TokenType.RETURN):
            return self.return_statement()
        else:
            return self.expression_statement()
    
    def assignment_or_expression(self) -> Statement:
        # Look ahead for assignment
        if self.position + 1 < len(self.tokens) and self.tokens[self.position + 1].type == TokenType.ASSIGN:
            name = self.current_token.value
            self.advance()  # consume identifier
            self.consume(TokenType.ASSIGN, "Expected ':='")
            value = self.expression()
            return Assignment(name, value)
        else:
            return self.expression_statement()
    
    def expression(self) -> Expression:
        return self.addition()
    
    def addition(self) -> Expression:
        expr = self.multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.current_token.value
            self.advance()
            right = self.multiplication()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def multiplication(self) -> Expression:
        expr = self.primary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE):
            operator = self.current_token.value
            self.advance()
            right = self.primary()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def primary(self) -> Expression:
        if self.match(TokenType.NUMBER):
            value = float(self.current_token.value)
            self.advance()
            return NumberLiteral(value)
        
        elif self.match(TokenType.STRING):
            value = self.current_token.value[1:-1]  # Remove quotes
            self.advance()
            return StringLiteral(value)
        
        elif self.match(TokenType.IDENTIFIER):
            name = self.current_token.value
            self.advance()
            
            # Check for function call
            if self.match(TokenType.LPAREN):
                self.advance()  # consume '('
                args = []
                
                while not self.match(TokenType.RPAREN):
                    args.append(self.expression())
                    if self.match(TokenType.COMMA):
                        self.advance()
                
                self.consume(TokenType.RPAREN, "Expected ')'")
                return FunctionCall(name, args)
            else:
                return Identifier(name)
        
        elif self.match(TokenType.LPAREN):
            self.advance()  # consume '('
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expected ')'")
            return expr
        
        else:
            self.error(f"Unexpected token: {self.current_token.value}")
```

### 4. Interpretador

```python
# linguagem/interpreter.py
from typing import Any, Dict, List, Optional
from .ast_nodes import *
from .environment import Environment
from .errors import RuntimeError
from .builtins import BUILTIN_FUNCTIONS

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        
        # Add built-in functions
        for name, func in BUILTIN_FUNCTIONS.items():
            self.globals.define(name, func)
    
    def interpret(self, program: Program) -> Any:
        result = None
        try:
            for statement in program.statements:
                result = self.execute(statement)
        except RuntimeError as error:
            print(f"Runtime Error: {error}")
            return None
        return result
    
    def execute(self, stmt: Statement) -> Any:
        return stmt.accept(self)
    
    def evaluate(self, expr: Expression) -> Any:
        return expr.accept(self)
    
    def visit_program(self, program: Program) -> Any:
        result = None
        for statement in program.statements:
            result = self.execute(statement)
        return result
    
    def visit_assignment(self, stmt: Assignment) -> None:
        value = self.evaluate(stmt.value)
        self.environment.define(stmt.name, value)
    
    def visit_if_statement(self, stmt: IfStatement) -> None:
        condition = self.evaluate(stmt.condition)
        
        if self.is_truthy(condition):
            for s in stmt.then_block:
                self.execute(s)
        elif stmt.else_block:
            for s in stmt.else_block:
                self.execute(s)
    
    def visit_while_loop(self, stmt: WhileLoop) -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            for s in stmt.body:
                self.execute(s)
    
    def visit_function_def(self, stmt: FunctionDef) -> None:
        function = LinguagemFunction(stmt, self.environment)
        self.environment.define(stmt.name, function)
    
    def visit_return_statement(self, stmt: ReturnStatement) -> Any:
        value = None
        if stmt.value:
            value = self.evaluate(stmt.value)
        raise Return(value)
    
    def visit_number_literal(self, expr: NumberLiteral) -> float:
        return expr.value
    
    def visit_string_literal(self, expr: StringLiteral) -> str:
        return expr.value
    
    def visit_identifier(self, expr: Identifier) -> Any:
        return self.environment.get(expr.name)
    
    def visit_binary_operation(self, expr: BinaryOperation) -> Any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        
        if expr.operator == '+':
            return left + right
        elif expr.operator == '-':
            return left - right
        elif expr.operator == '*':
            return left * right
        elif expr.operator == '/':
            if right == 0:
                raise RuntimeError("Division by zero")
            return left / right
        elif expr.operator == 'is':
            return left == right
        else:
            raise RuntimeError(f"Unknown operator: {expr.operator}")
    
    def visit_function_call(self, expr: FunctionCall) -> Any:
        function = self.environment.get(expr.name)
        
        arguments = []
        for arg in expr.arguments:
            arguments.append(self.evaluate(arg))
        
        if callable(function):  # Built-in function
            return function(*arguments)
        elif isinstance(function, LinguagemFunction):
            return function.call(self, arguments)
        else:
            raise RuntimeError(f"'{expr.name}' is not a function")
    
    def is_truthy(self, value: Any) -> bool:
        if value is None or value is False:
            return False
        if value is True:
            return True
        return bool(value)

class LinguagemFunction:
    def __init__(self, declaration: FunctionDef, closure: Environment):
        self.declaration = declaration
        self.closure = closure
    
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> Any:
        # Create new environment for function
        environment = Environment(self.closure)
        
        # Bind parameters
        for i, param in enumerate(self.declaration.parameters):
            if i < len(arguments):
                environment.define(param, arguments[i])
        
        # Execute function body
        previous = interpreter.environment
        try:
            interpreter.environment = environment
            
            for statement in self.declaration.body:
                interpreter.execute(statement)
        except Return as return_value:
            return return_value.value
        finally:
            interpreter.environment = previous
        
        return None  # Implicit return None

class Return(Exception):
    def __init__(self, value: Any):
        self.value = value
```

---

## 📦 Empacotamento

### 1. Versionamento Semântico

```python
# linguagem/__init__.py
__version__ = "1.0.0"
__author__ = "Seu Nome"
__email__ = "seu@email.com"
__license__ = "MIT"

# Versioning scheme: MAJOR.MINOR.PATCH
# MAJOR: Breaking changes
# MINOR: New features, backwards compatible  
# PATCH: Bug fixes, backwards compatible
```

### 2. MANIFEST.in

```plaintext
include LICENSE
include README.md
include CHANGELOG.md
include requirements.txt
include requirements-dev.txt
recursive-include linguagem *.py
recursive-include examples *.ext
recursive-include tests *.py
recursive-include docs *.md *.rst
recursive-include tools *
global-exclude __pycache__
global-exclude *.py[co]
global-exclude .DS_Store
global-exclude *.so
```

### 3. Builds e Distribuições

```bash
# Preparar ambiente de build
python -m pip install --upgrade pip setuptools wheel build twine

# Gerar distribuições
python -m build

# Resultado:
# dist/
# ├── minha_linguagem-1.0.0.tar.gz     # Source distribution
# └── minha_linguagem-1.0.0-py3-none-any.whl  # Wheel distribution

# Verificar distribuições
python -m twine check dist/*
```

---

## 🧪 Testes e Qualidade

### 1. Testes Unitários

```python
# tests/test_lexer.py
import pytest
from linguagem.lexer import Lexer
from linguagem.tokens import TokenType

class TestLexer:
    def test_numbers(self):
        lexer = Lexer("42 3.14")
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "42"
        assert tokens[1].type == TokenType.NUMBER
        assert tokens[1].value == "3.14"
    
    def test_keywords(self):
        lexer = Lexer("given otherwise")
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.IF
        assert tokens[1].type == TokenType.ELSE
    
    def test_assignment(self):
        lexer = Lexer("x := 10")
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[1].type == TokenType.ASSIGN
        assert tokens[2].type == TokenType.NUMBER

# tests/test_parser.py
import pytest
from linguagem.lexer import Lexer
from linguagem.parser import Parser
from linguagem.ast_nodes import *

class TestParser:
    def parse_source(self, source: str) -> Program:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()
    
    def test_assignment(self):
        program = self.parse_source("x := 42")
        
        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, Assignment)
        assert stmt.name == "x"
        assert isinstance(stmt.value, NumberLiteral)
        assert stmt.value.value == 42.0

# tests/test_interpreter.py  
import pytest
from linguagem.lexer import Lexer
from linguagem.parser import Parser
from linguagem.interpreter import Interpreter

class TestInterpreter:
    def run_source(self, source: str) -> Any:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        interpreter = Interpreter()
        return interpreter.interpret(program)
    
    def test_arithmetic(self):
        result = self.run_source("2 + 3 * 4")
        assert result == 14.0
    
    def test_assignment(self):
        interpreter = Interpreter()
        self.run_source("x := 10")
        assert interpreter.globals.get("x") == 10.0

# tests/test_examples.py
import pytest
import subprocess
import os

class TestExamples:
    def test_hello_world(self):
        result = subprocess.run(
            ["python", "-m", "linguagem", "run", "examples/01_hello.ext"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Hello, World!" in result.stdout
```

### 2. Configuração pytest

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts = 
    --verbose
    --cov=linguagem
    --cov-report=html
    --cov-report=term
    --cov-fail-under=80
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

### 3. Code Quality Tools

```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
        args: ["--profile", "black"]

# Instalar e configurar
pip install pre-commit
pre-commit install
```

---

## 📚 Documentação

### 1. README.md Profissional

```markdown
# 🚀 Minha Linguagem

[![PyPI version](https://badge.fury.io/py/minha-linguagem.svg)](https://badge.fury.io/py/minha-linguagem)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/usuario/minha-linguagem/workflows/Tests/badge.svg)](https://github.com/usuario/minha-linguagem/actions)

> Uma linguagem de programação revolucionária com sintaxe intuitiva

## ✨ Features

- 🎯 **Sintaxe Natural**: Palavras em português/inglês natural
- 🚀 **Alto Desempenho**: Built on Python, optimized for speed  
- 📊 **Data Science Ready**: Built-in data processing capabilities
- 🔧 **Python Interop**: Seamless integration with Python ecosystem

## 🚀 Quick Start

```bash
pip install minha-linguagem
```

```python
# hello.ext
saudar("Olá, mundo!")
```

```bash
minha-linguagem run hello.ext
```

[📖 Full Documentation](https://minha-linguagem.readthedocs.io) | [🎯 Tutorial](docs/tutorial.md) | [🔧 API Reference](docs/api.md)
```

### 2. Documentação Técnica

```markdown
# docs/language-specification.md

# Language Specification

## Grammar (BNF)

```bnf
program     ::= statement*
statement   ::= assignment | if_stmt | while_stmt | function_def | expression
assignment  ::= IDENTIFIER ":=" expression
if_stmt     ::= "given" expression ":" block ("orif" expression ":" block)* ("otherwise" ":" block)?
while_stmt  ::= "persist" expression ":" block  
function_def::= "action" IDENTIFIER "(" parameters? ")" ":" block
expression  ::= equality
equality    ::= comparison ( ("is" | "isnot") comparison )*
comparison  ::= addition ( ("bigger" | "smaller" | "biggerequal" | "smallerequal") addition )*
addition    ::= multiplication ( ("+" | "-") multiplication )*
multiplication ::= unary ( ("*" | "/") unary )*
unary       ::= ("not" | "-") unary | primary
primary     ::= NUMBER | STRING | IDENTIFIER | "(" expression ")" | function_call
```

## Keywords

| Keyword | Python Equivalent | Description |
|---------|------------------|-------------|
| `given` | `if` | Conditional statement |
| `orif` | `elif` | Else if |
| `otherwise` | `else` | Else clause |
| `persist` | `while` | While loop |
| `cycle` | `for` | For loop |
| `action` | `def` | Function definition |
| `yield` | `return` | Return statement |
| `blueprint` | `class` | Class definition |
```

### 3. Tutorial Interativo

```markdown
# docs/tutorial.md

# Tutorial: Primeiro Programa

## 1. Hello World

```ext
// Seu primeiro programa
saudar("Olá, mundo!")
```

## 2. Variáveis

```ext  
// Declarando variáveis
nome := "João"
idade := 25
ativo := verdadeiro

// Usando variáveis
saudar("Olá, " + nome)
saudar("Você tem " + idade + " anos")
```

## 3. Condicionais

```ext
idade := 18

dado idade >= 18:
    saudar("Maior de idade")
senao:
    saudar("Menor de idade")
```
```

---

## 📡 Publicação no PyPI

### 1. Preparação da Conta PyPI

```bash
# Criar conta em:
# https://pypi.org/account/register/
# https://test.pypi.org/account/register/ (para testes)

# Configurar credenciais
pip install keyring
keyring set https://upload.pypi.org/legacy/ __token__
# Enter your token when prompted
```

### 2. Build e Upload

```bash
# 1. Preparar ambiente
python -m pip install --upgrade build twine

# 2. Limpar builds anteriores
rm -rf dist/ build/ *.egg-info/

# 3. Gerar distribuições
python -m build

# 4. Verificar pacotes
python -m twine check dist/*

# 5. Testar no PyPI Test (recomendado)
python -m twine upload --repository testpypi dist/*

# 6. Testar instalação
pip install --index-url https://test.pypi.org/simple/ minha-linguagem

# 7. Upload para PyPI definitivo
python -m twine upload dist/*
```

### 3. Configuração .pypirc

```ini
# ~/.pypirc
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIc... (seu token)

[testpypi]  
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIc... (seu token de teste)
```

---

## 🔄 GitHub e Controle de Versão

### 1. Estrutura de Branches

```bash
# Branch model
main          # Versão estável de produção
develop       # Development branch  
feature/*     # Feature branches
hotfix/*      # Bug fixes urgentes
release/*     # Preparação de releases
```

### 2. Conventional Commits

```bash
# Formato: <type>(<scope>): <description>
feat(lexer): add support for unicode identifiers
fix(parser): resolve precedence issue with binary operators  
docs: update installation instructions
test: add integration tests for REPL
refactor(interpreter): improve error handling
perf: optimize AST traversal
ci: add automated publishing workflow
```

### 3. Release Process

```bash
# 1. Create release branch
git checkout -b release/1.1.0 develop

# 2. Update version numbers
# - setup.py
# - __init__.py  
# - CHANGELOG.md

# 3. Test release candidate
python -m pytest
python -m build
python -m twine check dist/*

# 4. Merge to main
git checkout main
git merge release/1.1.0

# 5. Tag release
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0

# 6. Merge back to develop
git checkout develop
git merge release/1.1.0
```

---

## 🤖 CI/CD e Automação

### 1. GitHub Actions - Tests

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Lint with flake8
      run: |
        flake8 linguagem tests
    
    - name: Type check with mypy
      run: |
        mypy linguagem
    
    - name: Test with pytest
      run: |
        pytest --cov=linguagem --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### 2. Automatic Publishing

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

### 3. Documentation Deployment

```yaml
# .github/workflows/docs.yml
name: Deploy Documentation

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install mkdocs mkdocs-material
    
    - name: Deploy docs
      run: mkdocs gh-deploy --force
```

---

## 📢 Marketing e Comunidade

### 1. Plataformas de Divulgação

#### GitHub
- ⭐ **README atrativo**: Logo, badges, GIFs demonstrativos
- 📝 **Issues/Discussions**: Comunidade ativa
- 🏷️ **Topics**: Adicionar tags relevantes
- 📊 **GitHub Pages**: Site do projeto

#### Redes Sociais
- 🐦 **Twitter**: Updates e demos
- 💼 **LinkedIn**: Artigos técnicos
- 🎥 **YouTube**: Tutoriais e demos
- 📝 **Dev.to**: Blog posts técnicos

#### Plataformas Técnicas
- 🔗 **Hacker News**: Submit com timing certo
- 🎯 **Reddit**: r/programming, r/Python
- 📰 **Stack Overflow**: Responder questões relacionadas
- 🏆 **Product Hunt**: Launch da linguagem

### 2. Conteúdo de Marketing

#### Blog Posts
```markdown
1. "Introducing MyLanguage: A New Way to Think About Programming"
2. "How to Build a Programming Language in Python"  
3. "MyLanguage vs Python: Performance Comparison"
4. "Building a Community Around Open Source Languages"
```

#### Demos e Videos
```markdown
- 🎬 "MyLanguage in 100 Seconds"
- 🔧 "Building a Web Server in MyLanguage"  
- 📊 "Data Analysis Made Simple"
- 🎮 "Creating Games with MyLanguage"
```

### 3. Comunidade

#### Canais de Comunicação
```markdown
- 💬 Discord/Slack server
- 📧 Mailing list  
- 💬 GitHub Discussions
- 🐦 Twitter hashtag #MyLanguage
```

#### Programas de Engajamento
```markdown
- 🏆 Contribute-a-thon events
- 🎓 Educational workshops
- 🎁 Sticker/swag programs
- 👥 Mentorship programs
```

---

## 🛠️ Manutenção e Evolução

### 1. Release Cycle

```markdown
## Release Schedule

### Major Releases (x.0.0)
- **Frequency**: Every 6-12 months
- **Content**: Breaking changes, major features
- **Planning**: 3 months ahead
- **Beta Period**: 1 month

### Minor Releases (x.y.0)  
- **Frequency**: Every 2-3 months
- **Content**: New features, improvements
- **Beta Period**: 2 weeks

### Patch Releases (x.y.z)
- **Frequency**: As needed
- **Content**: Bug fixes, security updates
- **Turnaround**: Within 48 hours for security
```

### 2. Issue Triage

```markdown
## Issue Labels

### Priority
- 🔥 `critical` - Security issues, data loss
- 🚨 `high` - Major functionality broken  
- 📋 `medium` - Important but not blocking
- 📝 `low` - Nice to have, documentation

### Type  
- 🐛 `bug` - Something is broken
- ✨ `enhancement` - New feature request
- 📚 `documentation` - Docs related
- 🎯 `good-first-issue` - For new contributors
```

### 3. Backwards Compatibility

```python
# Deprecation strategy
import warnings

def old_function():
    warnings.warn(
        "old_function is deprecated, use new_function instead",
        DeprecationWarning,
        stacklevel=2
    )
    return new_function()

# Version compatibility matrix
SUPPORTED_VERSIONS = {
    "1.x": "2025-12-31",  # End of support
    "2.x": "2026-12-31",
    "3.x": "Current"
}
```

### 4. Performance Monitoring

```python
# benchmarks/performance_suite.py
import time
import psutil
import pytest

class PerformanceBenchmark:
    def test_parsing_speed(self):
        large_program = "x := 1\n" * 10000
        
        start = time.time()
        # Parse program
        end = time.time()
        
        parse_time = end - start
        assert parse_time < 1.0, f"Parsing too slow: {parse_time}s"
    
    def test_memory_usage(self):
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Run interpreter
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        max_allowed = 100 * 1024 * 1024  # 100MB
        assert memory_increase < max_allowed
```

---

## 🎯 Checklist de Lançamento

### ✅ Pré-Lançamento

#### Código
- [ ] Lexer implementado e testado
- [ ] Parser implementado e testado  
- [ ] Interpretador/Transpilador funcional
- [ ] Biblioteca padrão básica
- [ ] CLI funcional (`--help`, `run`, `repl`)
- [ ] Exemplos funcionando
- [ ] Testes com cobertura >80%

#### Documentação
- [ ] README.md profissional
- [ ] Tutorial de instalação
- [ ] Exemplos de código
- [ ] Referência da linguagem
- [ ] API documentation
- [ ] CHANGELOG.md

#### Qualidade
- [ ] Linting (flake8, black)
- [ ] Type checking (mypy)
- [ ] Security scanning
- [ ] Performance benchmarks
- [ ] Cross-platform testing

#### Legal
- [ ] Licença escolhida (MIT recomendada)
- [ ] Copyright notices
- [ ] Contributor guidelines
- [ ] Code of conduct

### 🚀 Lançamento

#### PyPI
- [ ] Conta PyPI criada
- [ ] Tokens configurados
- [ ] TestPyPI testado
- [ ] Upload para PyPI
- [ ] Instalação verificada

#### GitHub
- [ ] Repositório público
- [ ] Release criada
- [ ] Tags versionadas
- [ ] GitHub Pages ativo
- [ ] Issues/Discussions habilitados

#### CI/CD
- [ ] GitHub Actions configuradas
- [ ] Tests automatizados
- [ ] Build verification
- [ ] Auto-publishing
- [ ] Documentation deployment

### 📈 Pós-Lançamento

#### Marketing
- [ ] Anúncio nas redes sociais
- [ ] Blog post de lançamento
- [ ] Submit para Hacker News
- [ ] Reddit posts
- [ ] Dev.to article

#### Comunidade
- [ ] Discord/Slack server
- [ ] Responder a feedback inicial
- [ ] Fix bugs urgentes
- [ ] Roadmap público
- [ ] Contributors guide

#### Monitoramento
- [ ] Analytics configurados
- [ ] Error tracking
- [ ] Performance monitoring
- [ ] Usage statistics
- [ ] User feedback collection

---

## 🎉 Conclusão

Criar e publicar uma linguagem de programação é um projeto ambicioso que requer:

1. **Planejamento cuidadoso** da sintaxe e semântica
2. **Implementação robusta** do compilador/interpretador
3. **Testes abrangentes** e controle de qualidade
4. **Documentação excelente** para adoção
5. **Estratégia de marketing** para ganhar tração
6. **Comunidade ativa** para sustentabilidade

### 🏆 Fatores de Sucesso

- **Resolver um problema real**: Sua linguagem deve ter um propósito claro
- **Experiência do desenvolvedor**: Priorize facilidade de uso
- **Documentação exemplar**: Tutoriais, exemplos e referências
- **Performance adequada**: Velocidade suficiente para casos de uso
- **Comunidade engajada**: Contributors e usuários ativos
- **Evolução constante**: Melhorias baseadas em feedback

### 🚀 Próximos Passos

1. **Defina sua visão**: Qual problema sua linguagem resolve?  
2. **Crie um MVP**: Implementação básica funcional
3. **Documente tudo**: README, tutoriais, exemplos
4. **Publique cedo**: Obtenha feedback rapidamente
5. **Itere rapidamente**: Melhore baseado no uso real
6. **Construa comunidade**: Engaje usuários e contributors

**Lembre-se**: Linguagens de programação bem-sucedidas são construídas ao longo do tempo, com dedicação e comunidade. Foque na qualidade, simplicidade e resolução de problemas reais.

---

**Boa sorte em sua jornada de criação de linguagens! 🚀**

*Este guia é baseado nas melhores práticas da indústria e na experiência de projetos como DataForge, TypeScript, Kotlin e outras linguagens modernas.*