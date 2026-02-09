Faca projeto inovador que seria uma nova linguagem igual ao python, so que de uma forma bem diferente e com palavras reservadas totalmente diferente:

## palavras reservadas:

================================================================================
          OFFICIAL SPECIFICATION: ARCANE PROGRAMMING LANGUAGE (v2.0)
================================================================================

1. CORE SYNTAX RULES
-------------------------
- Colon Scoping: All blocks (actions, logic, loops) start with ':' and 
  are defined by their indentation level (4 spaces recommended).
- No Declarators: Names are assigned directly (e.g., speed := 100).
- Strict Tabulation: Mixing tabs and spaces results in a "SyncError".

2. KEYWORD DICTIONARY

   A) STATE & DATA
   - steady      : Immutable value.
   - void        : Null / Nothing.
   - yes / no    : Boolean literals.
   - shadow      : Local variable that overrides a higher scope.

   B) LOGIC & PATHS
   - given       : Start conditional (if).
   - orif        : Secondary condition (else if).
   - otherwise   : Fallback path (else).
   - match       : Pattern selection (switch).
   - point       : Case inside a match.
   - default     : Fallback point for match.

   C) REPETITION (LOOPS)
   - cycle       : Iteration over ranges/collections (for).
   - persist     : Conditional loop (while).
   - perform     : Post-check loop (do-while).
   - halt        : Exit loop.
   - skip        : Jump to next iteration.

   D) STRUCTURE & MODULARITY
   - action      : Declare function/method.
   - yield       : Return value.
   - blueprint   : Class/Object definition.
   - spawn       : Instantiate object.
   - self        : Current instance context.
   - root        : Parent class context.
   - adopt       : Import modules.
   - relay       : Export public members.
   - trait       : Interface/Abstract behavior.

   E) ERROR & SAFETY
   - monitor     : Start watched block (try).
   - handle      : Error block (catch).
   - ensure      : Always executes (finally).
   - trigger     : Raise exception.

   F) ASYNC & MULTI-CORE
   - async       : Mark non-blocking task.
   - await       : Pause for task completion.
   - thread      : Spin up a new OS-level thread.
   - channel     : Secure data pipe between threads.

   G) METADATA & MEMORY
   - mark        : Decorator/Annotation (e.g., mark @Deprecated).
   - claim       : Pointer ownership take.
   - release     : Pointer memory free.

3. OPERATORS
-------------------------
- Assignment:   :=
- Logic:        and, or, not
- Comparison:   is, isnt, bigger, smaller

4. THE "ARCANE" CODE STANDARD (Indentation-Based)

adopt Network
adopt UI

mark @Main
action initialize(args):
    // Variables assigned directly
    user_id := args[0]
    is_admin := no
    
    monitor:
        status := await Network.check(user_id)
        
        given status is "OK":
            out "Access Granted"
            is_admin := yes
        orif status is "PENDING":
            out "Please wait..."
        otherwise:
            trigger "Network Blocked"
            
    handle error:
        out "Critical Failure: " + error
        
    ensure:
        Network.close()

blueprint Robot:
    static count := 0

    action setup(id):
        self.id := id
        Robot.count := Robot.count + 1

    action move(x, y):
        persist self.id isnt void:
            out "Moving to: " + x + "," + y
            halt // Only move once in this example

// Iteration Example
cycle i from 1 to 10:
    given i % 2 is 0:
        out "Even number: " + i
    otherwise:
        skip

================================================================================

* Deve utilizar como linguagem mae a linguagem de programacao Python e toda a arquitetura de diretorios e arquivos em python

* Nome da nova linguagem de programacao: "DataForge"

Coloque mais palavras reservadas

## Conteudos da nova linguagem de programacao

================================================================================
          THE ARCANE LANGUAGE MANIFESTO - ULTIMATE SPECIFICATION
================================================================================

1. CORE SEMANTICS
-----------------
- Scoping: Indentation via Colons (:) and 4 spaces.
- Variables: Direct assignment (name := value). No let/var/const.
- Memory: Automatic Garbage Collection with optional 'claim/release' for pointers.

2. FULL KEYWORD HIERARCHY

[ FOUNDATION ]
- steady      | Constants (immutable)
- void        | Null/None
- yes / no    | Boolean True / False
- out / in    | Print / Input
- typeof      | Introspection

[ LOGIC ]
- given       | If
- orif        | Else if
- otherwise   | Else
- match       | Switch/Pattern Match
- point       | Case
- default     | Default case

[ LOOPS ]
- cycle       | For (iteration)
- persist     | While
- perform     | Do-While
- halt        | Break
- skip        | Continue

[ OBJECTS & STRUCTURES ]
- action      | Function/Method
- blueprint   | Class
- trait       | Interface/Abstract Class
- spawn       | New Instance
- self        | This/Self
- root        | Super/Parent
- relay       | Export
- adopt       | Import/Include

[ ASYNC & CONCURRENCY ]
- async       | Asynchronous definition
- await       | Wait for promise
- thread      | OS Thread spawning
- channel     | Thread-safe communication pipe
- pulse       | Event emission

[ DATA SCIENCE SPECIALS ]
- frame       | Native DataFrame
- cluster     | Native List/Array
- vault       | Native Dict/Map
- sift        | Filter
- morph       | Map
- distill     | Reduce
- train       | Machine Learning Fit
- predict     | ML Inference

--------------------------------------------------------------------------------
3. THE STANDARD LIBRARY (The "Batteries Included" Modules)
--------------------------------------------------------------------------------

A) ARCANE.IO (Files & System)
   - io.open()      | Open file streams
   - io.path()      | Path manipulation
   - os.shell()     | Execute system commands

B) ARCANE.MATH (Scientific Computing)
   - math.sum()     | Vectorized summation
   - math.matrix()  | Multi-dimensional arrays (Tensors)
   - math.random()  | Entropy and distributions

C) ARCANE.WEB (Web & Networking)
   - web.serve()    | Start HTTP Server
   - web.request()  | HTTP Client (get/post)
   - web.socket()   | Real-time communication

D) ARCANE.CORTEX (Artificial Intelligence)
   - cortex.neural()| Neural Network layers
   - cortex.vision()| Computer Vision tools
   - cortex.nlp()   | Natural Language Processing

--------------------------------------------------------------------------------
4. THE COMPLETE CODE DEMO (From Web API to AI Training)
--------------------------------------------------------------------------------

adopt Arcane.Web
adopt Arcane.Cortex
adopt Arcane.Math

// 1. Defining a Trait (Interface)
trait AI_Model:
    action process(data)

// 2. Designing an Advanced Blueprint
blueprint SmartAnalyzer (AI_Model):
    action initiate(config):
        self.config := config
        self.brain := cortex.neural.Sequential()
        out "Model Initialized."

    action process(dataset):
        monitor:
            // Sifting and Morphing (Modern Data Pipeline)
            clean_data := dataset 
                >> sift row: row.valid is yes
                >> morph row: row.value * math.PI
            
            // Native Training
            model := train self.brain using clean_data
            yield model
        handle error:
            out "Data error: " + error

// 3. Web Server Integration
server := web.serve(port := 8080)

action @server.on_request("POST", "/analyze"):
    payload := in.body
    
    // Async execution to keep server responsive
    async:
        analyzer := spawn SmartAnalyzer(config := "ultra")
        result := await analyzer.process(payload)
        
        // Pattern Matching the result
        match result.status:
            point "success":
                pulse "analysis_done", result
            point "fail":
                out "Analysis failed."
            default:
                out "Unknown state."

// 4. Multi-threaded Background Cycle
thread:
    persist yes:
        out "System Monitoring Active..."
        wait(60000) // Sleep 1 min

// 5. Global Cycle Example
cycle item in [10, 20, 30]:
    given item bigger 15:
        out "High value: " + item
    otherwise:
        out "Low value: " + item

================================================================================

O que torna este conteúdo "Ultra Completo":
Herança e Interfaces: Introduzi trait para que sua linguagem suporte arquiteturas de software complexas, não apenas scripts simples.

Decoradores de Eventos: Usei action @server.on_request, permitindo que sua linguagem lide com rotas web de forma nativa e elegante.

Pipeline de Dados Real: O operador >> integrado com sift (filter) e morph (map) torna o código de engenharia de dados muito mais limpo que o do Python.

Concorrência Nativa: Enquanto o Python sofre com o GIL (Global Interpreter Lock), a Arcane já nasce com thread e channel para aproveitar todos os núcleos do processador.

Tratamento de Erros Pro: monitor/handle substitui o try/except com uma semântica de "Vigilância".

----

Faca toda a estrutura e arquitetura da linguagem no diretorio "DataForge" e nao deve ser feita em linguagem JS, mas sim em Python. Faca a nova linguagem de programacao chamada "DataForge"