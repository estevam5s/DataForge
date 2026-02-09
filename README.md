# DataForge Programming Language

> **A revolutionary programming language built on Python — with a completely unique syntax and reserved words.**

```
================================================================================
     ____        _        _____                    
    |  _ \  __ _| |_ __ _|  ___|__  _ __ __ _  ___ 
    | | | |/ _` | __/ _` | |_ / _ \| '__/ _` |/ _ \
    | |_| | (_| | || (_| |  _| (_) | | | (_| |  __/
    |____/ \__,_|\__\__,_|_|  \___/|_|  \__, |\___|
                                         |___/      
================================================================================
```

## 🚀 Installation

```bash
cd DataForge
pip install -e .
```

## 🔥 Usage

### Run a DataForge file (.df)
```bash
dataforge run examples/hello.df
```

### Interactive REPL
```bash
dataforge repl
```

### Show version
```bash
dataforge version
```

## 📖 Language Syntax

### Variables
```
name := "DataForge"
age := 25
pi := 3.14159
active := yes
empty := void
```

### Constants
```
steady MAX_SIZE := 1024
```

### Output & Input
```
out "Hello, World!"
user_name := in "What is your name? "
```

### Conditionals
```
given age bigger 18:
    out "Adult"
orif age is 18:
    out "Just turned 18"
otherwise:
    out "Minor"
```

### Pattern Matching
```
match status:
    point "OK":
        out "All good"
    point "ERROR":
        out "Something failed"
    default:
        out "Unknown"
```

### Loops
```
cycle i from 1 to 10:
    out i

cycle item in [1, 2, 3]:
    out item

persist running is yes:
    out "Still running..."
    halt
```

### Functions
```
action greet(name):
    yield "Hello, " + name

result := greet("World")
out result
```

### Classes
```
blueprint Animal:
    action setup(name, sound):
        self.name := name
        self.sound := sound

    action speak():
        out self.name + " says " + self.sound

cat := spawn Animal("Cat", "Meow")
cat.speak()
```

### Traits (Interfaces)
```
trait Drawable:
    action draw()

blueprint Circle (Drawable):
    action setup(radius):
        self.radius := radius

    action draw():
        out "Drawing circle with radius " + self.radius
```

### Error Handling
```
monitor:
    risky_operation()
handle error:
    out "Error: " + error
ensure:
    cleanup()
```

### Async/Await
```
async action fetch_data(url):
    result := await web.request(url)
    yield result
```

### Data Science Pipelines
```
data := frame [[1,2],[3,4],[5,6]]
filtered := data >> sift row: row[0] bigger 2
transformed := filtered >> morph row: row[0] * 2
```

### Imports
```
adopt Arcane.Math
adopt Arcane.Web
```

## 📁 File Extension
DataForge files use the `.df` extension.

## 🏗️ Architecture
```
DataForge/
├── dataforge/
│   ├── __init__.py          # Package init
│   ├── cli.py               # Command-line interface
│   ├── lexer.py             # Tokenizer
│   ├── tokens.py            # Token definitions
│   ├── ast_nodes.py         # AST node classes
│   ├── parser.py            # Parser (tokens → AST)
│   ├── interpreter.py       # Tree-walking interpreter
│   ├── environment.py       # Scope/Environment manager
│   ├── errors.py            # Custom error types
│   ├── repl.py              # Interactive REPL
│   ├── builtins.py          # Built-in functions
│   └── stdlib/              # Standard Library
│       ├── __init__.py
│       ├── arcane_io.py     # File I/O
│       ├── arcane_math.py   # Math operations
│       ├── arcane_web.py    # Web/HTTP
│       ├── arcane_cortex.py # AI/ML
│       └── arcane_data.py   # Data Science
├── examples/                # Example programs
├── tests/                   # Test suite
├── setup.py
└── README.md
```

## 📜 License
MIT License
