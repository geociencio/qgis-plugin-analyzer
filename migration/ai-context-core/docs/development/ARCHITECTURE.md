
# Architecture Overview

`ai-context-core` is designed as a modular, high-performance static analysis tool specifically tailored to provide context for AI coding assistants.

## 🏗️ Core Components

The system is built around a unidirectional data flow pipeline:

```mermaid
graph TD
    CLI[CLI (ai-ctx)] --> Config[Config Loader]
    Config --> Engine[Analysis Engine]
    Engine --> FS[File System Utils]
    FS --> AST[AST Analyzers]
    FS --> Deps[Dependency Analyzer]
    AST --> Metrics[Metrics Engine]
    Deps --> Metrics
    Metrics --> Reporting[Reporting Engine]
    Reporting --> Artifacts[Context Artifacts]
```

### 1. Engine (`analyzer/engine.py`)
The orchestrator. It initializes the analysis process, manages parallel workers (using `ProcessPoolExecutor`), and aggregates results. It ensures thread safety and handles timeouts for large projects.

### 2. File System Utilities (`analyzer/fs_utils.py`)
Optimized I/O layer.
- **Memory Mapping**: Uses `mmap` for reading large files efficiently.
- **LRU Cache**: Caches file content to avoid redundant reads during multi-pass analysis.
- **Intelligent Filtering**: Respects `.analyzerignore` and handles standard exclusion patterns automatically.

### 3. AST Analysis (`analyzer/ast_utils.py`)
The brain of the operation. Unlike tools that require runtime execution, we use Python's `ast` module to perform **static analysis**.
- **Benefits**: Secure (no code execution), fast, and works on broken/incomplete code.
- **Capabilities**: Extracts class hierarchies, function signatures, docstring coverage, and type hint statistics.

### 4. Dependency Graph (`analyzer/dependencies.py`)
Builds a directed graph of imports to understand project coupling.
- Detects circular dependencies (DFS).
- Calculates graph metrics (density, connected components).
- Categorizes imports (Internal vs. External vs. StdLib).

### 5. Profile System (`config/`)
Allows behavior customization without changing code.
- **YAML-based**: Profiles are simple YAML files.
- **Rule Engine**: Thresholds for "quality" are defined per-profile (e.g., QGIS plugins have different valid sizes than Microservices).

## 🔒 Security & Performance Principles

1.  **Static First**: We never `import` the user's code. We parse it. This prevents side effects and allows analyzing hostile code safely.
2.  **Fail Gracefully**: If a module has syntax errors, we log it and continue. One bad file shouldn't stop the analysis.
3.  **Context-Aware**: The output isn't just "metrics"; it's formatted specifically to be consumed by LLMs (Markdown optimized for token density).
