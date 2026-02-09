================================================================================
          OFFICIAL SPECIFICATION: DATAFORGE PROGRAMMING LANGUAGE (v2.0)
================================================================================

1. CORE SYNTAX RULES
-------------------------
- Colon Scoping: All blocks (actions, logic, loops) start with ':' and 
  are defined by their indentation level (4 spaces recommended).
- No Declarators: Names are assigned directly (e.g., speed := 100).
- Strict Tabulation: Mixing tabs and spaces results in a "SyncError".
- Comments: // single-line, # single-line, /* block */
- File Extension: .df

2. FULL KEYWORD DICTIONARY (80+ Reserved Words)

   A) FOUNDATION
   ┌─────────────┬──────────────────────────────────┐
   │ steady      │ Immutable constant               │
   │ void        │ Null / Nothing                    │
   │ yes / no    │ Boolean literals (true/false)     │
   │ out         │ Print to stdout                   │
   │ in          │ Read from stdin                   │
   │ typeof      │ Type introspection                │
   │ shadow      │ Local variable override           │
   └─────────────┴──────────────────────────────────┘

   B) LOGIC & CONDITIONALS
   ┌─────────────┬──────────────────────────────────┐
   │ given       │ If                                │
   │ orif        │ Else if                           │
   │ otherwise   │ Else                              │
   │ match       │ Pattern matching (switch)         │
   │ point       │ Case in match                     │
   │ default     │ Default case                      │
   │ and         │ Logical AND                       │
   │ or          │ Logical OR                        │
   │ not         │ Logical NOT                       │
   │ is          │ Equality comparison               │
   │ isnt        │ Inequality comparison             │
   │ bigger      │ Greater than                      │
   │ smaller     │ Less than                         │
   │ bigger_eq   │ Greater than or equal             │
   │ smaller_eq  │ Less than or equal                │
   └─────────────┴──────────────────────────────────┘

   C) LOOPS & REPETITION
   ┌─────────────┬──────────────────────────────────┐
   │ cycle       │ For loop (iteration)             │
   │ persist     │ While loop                        │
   │ perform     │ Do-while loop                     │
   │ halt        │ Break                             │
   │ skip        │ Continue                          │
   │ from        │ Range start                       │
   │ to          │ Range end                         │
   │ step        │ Range step                        │
   └─────────────┴──────────────────────────────────┘

   D) STRUCTURE & MODULARITY
   ┌─────────────┬──────────────────────────────────┐
   │ action      │ Function / Method                 │
   │ yield       │ Return value                      │
   │ blueprint   │ Class / Object definition         │
   │ trait       │ Interface / Abstract behavior      │
   │ spawn       │ Create new instance               │
   │ self        │ Current instance reference         │
   │ root        │ Parent class reference             │
   │ adopt       │ Import module                     │
   │ relay       │ Export members                     │
   │ static      │ Static class member               │
   │ abstract    │ Abstract method marker             │
   └─────────────┴──────────────────────────────────┘

   E) ERROR HANDLING
   ┌─────────────┬──────────────────────────────────┐
   │ monitor     │ Try block                         │
   │ handle      │ Catch block                       │
   │ ensure      │ Finally block                     │
   │ trigger     │ Raise exception                   │
   └─────────────┴──────────────────────────────────┘

   F) ASYNC & CONCURRENCY
   ┌─────────────┬──────────────────────────────────┐
   │ async       │ Asynchronous definition           │
   │ await       │ Wait for async completion         │
   │ thread      │ OS-level thread                   │
   │ channel     │ Thread-safe data pipe             │
   │ pulse       │ Event emission                    │
   └─────────────┴──────────────────────────────────┘

   G) METADATA & MEMORY
   ┌─────────────┬──────────────────────────────────┐
   │ mark        │ Decorator / Annotation            │
   │ claim       │ Pointer ownership                 │
   │ release     │ Pointer memory free               │
   └─────────────┴──────────────────────────────────┘

   H) DATA SCIENCE
   ┌─────────────┬──────────────────────────────────┐
   │ frame       │ Native DataFrame                  │
   │ cluster     │ Native List/Array                  │
   │ vault       │ Native Dict/Map                   │
   │ sift        │ Filter (pipeline)                 │
   │ morph       │ Map (pipeline)                     │
   │ distill     │ Reduce (pipeline)                 │
   │ train       │ ML training                       │
   │ predict     │ ML inference                      │
   └─────────────┴──────────────────────────────────┘

   I) EXTRA KEYWORDS
   ┌─────────────┬──────────────────────────────────┐
   │ using       │ Context specification             │
   │ with        │ Context manager                   │
   │ as          │ Alias                             │
   │ range       │ Range function                    │
   │ wait        │ Sleep/delay                       │
   │ emit        │ Event emission                    │
   │ listen      │ Event listener                    │
   │ each        │ Each iteration                    │
   │ forge       │ Create/build                      │
   │ link        │ Connect                           │
   │ unlink      │ Disconnect                        │
   │ freeze      │ Make immutable                    │
   │ thaw        │ Make mutable again                │
   │ cast        │ Type conversion                   │
   │ inspect     │ Debug inspection                  │
   │ assert      │ Assertion                         │
   │ delete      │ Delete variable/element           │
   │ exists      │ Check existence                   │
   └─────────────┴──────────────────────────────────┘

3. OPERATORS
-------------------------
- Assignment:    :=
- Arithmetic:    +  -  *  /  %  **  //
- Comparison:    is  isnt  bigger  smaller  bigger_eq  smaller_eq  ==  !=
- Logic:         and  or  not
- Pipeline:      >>
- Member:        .
- Index:         []
- Grouping:      ()

4. STANDARD LIBRARY
-------------------------
- Arcane.IO      : File I/O, system operations
- Arcane.Math    : Mathematics, statistics, matrices
- Arcane.Web     : HTTP server/client, sockets
- Arcane.Cortex  : AI/ML, neural networks, NLP
- Arcane.Data    : DataFrames, data analysis

5. BUILT-IN FUNCTIONS (50+)
-------------------------
Type:       len, type, str, int, float, bool, cluster, vault, range, cast
Math:       abs, min, max, sum, round, floor, ceil, sqrt, pow, log, sin, cos, tan
Random:     random, randint, choice, shuffle
Collection: sorted, reversed, enumerate, zip, append, pop, insert, remove,
            keys, values, items, contains, flatten, unique, count, index, slice
String:     join, split, strip, upper, lower, replace, startswith, endswith, find, format
Functional: map, filter, reduce
Time:       time, sleep
Utility:    exists, freeze, thaw, hash, id
Constants:  PI, E, TAU, INF, NAN

================================================================================
