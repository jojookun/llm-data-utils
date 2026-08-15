# Architecture

This document defines the architectural principles, package responsibilities, dependency boundaries, and import conventions for `llm-data-utils`.

---

## Design Goals

The architecture of `llm-data-utils` is designed around the following core engineering goals:

1. **Modularity**: Distinct functional concerns are partitioned into isolated, self-contained subpackages.
2. **Provider Independence**: Core text processing, data contracts, and computational algorithms operate independently of any specific LLM provider or external cloud service.
3. **Predictable Imports**: Clean and explicit module hierarchies make symbol locations obvious to developers.
4. **Low Coupling & High Cohesion**: Internal components interact through well-defined contracts without unnecessary bidirectional dependencies.
5. **Testability**: Pure computational and text functions can be unit-tested without mocking third-party network APIs or heavy dependencies.
6. **Extensibility**: Future integrations (such as Google Gemini, Antigravity, or MCP servers) can be added as boundary adapters without modifying or contaminating core logic.

---

## Package Responsibilities

### Current Packages (Core Development Phase)

* **`models`**
  * **Purpose**: Shared data contracts, domain entities, and reusable type structures (e.g., dataclasses, typed dictionaries, protocols).
  * **Constraint**: Must remain foundational and close to pure Python. Must never depend on provider-specific integrations or high-level orchestration layers.

* **`text`**
  * **Purpose**: String manipulation, normalization, transformation, token/chunk handling, and text search utilities.
  * **Constraint**: Pure algorithms and string utilities. Must not depend on Gemini, Antigravity, or external cloud services.

* **`compute`**
  * **Purpose**: Provider-independent computational routines, metrics, and numerical helpers.
  * **Constraint**: General-purpose computation. Must not contain LLM-specific logic or network dependencies.

* **`core`**
  * **Purpose**: Reusable processing abstractions, pipeline coordination, and configuration management.
  * **Constraint**: Coordinates internal utilities without becoming an unorganized dumping ground.

### Planned Packages (Future Integration Phases)

> **Note**: In alignment with YAGNI principles, the following packages are planned but intentionally not physically created on Day 4.

* **`llm`** *(Planned)*
  * **Future Responsibility**: Provider-agnostic LLM interface abstractions, prompt execution contracts, structured output parsing, and resilience mechanisms (retries, rate limiting).
  * **Dependency Boundary**: May consume `core`, `models`, and `text`. Lower-level foundational packages (`models`, `text`, `compute`) must never depend on `llm`.

* **`adapters`** *(Planned)*
  * **Future Responsibility**: Concrete third-party integrations, including Google Gemini SDK bindings, Antigravity integration, and MCP tool protocols.
  * **Dependency Boundary**: Adapters reside at the outermost architectural boundary. Adapters may depend on internal packages, but internal library code must never import or depend on specific adapters.

---

## Dependency Direction

Dependencies must strictly flow downward from high-level integrations to low-level foundations:

```text
adapters (Planned)
   ↓
  llm (Planned)
   ↓
 core
 ↙   ↘
text compute
 ↘   ↙
 models
```

> **Permitted vs. Mandatory Dependencies**: This diagram defines *permitted* dependency flow, not mandatory couplings. Higher-level packages are never required to import lower-level packages unless genuinely needed by the concrete implementation. For example, a pure string-manipulation routine in `text` does not need to import `models` simply because `models` is architecturally below `text`.
>
> **Core Principle**: *Depend downward only when needed; never depend upward.*

### Architectural Dependency Rules

1. **Foundational Integrity**: `models` is the base layer and has zero internal dependencies.
2. **Provider Isolation**: `text` and `compute` remain strictly provider-independent.
3. **Internal Orchestration**: `core` may coordinate `text`, `compute`, and `models`.
4. **LLM Layering**: `llm` sits above `core` and utilizes lower-level utilities.
5. **Outer Boundary Adapters**: External services reside exclusively in `adapters`.
6. **No Inward Inversions**: Foundational packages must never import concrete external adapters.
7. **No Circular Imports**: Cycles between modules or packages are prohibited.
8. **Boundary Containment**: Provider SDK imports (e.g. Gemini) are isolated within adapter modules.

#### Anti-Pattern Example (Violation)

```text
[models.data_container] ---> imports ---> [adapters.gemini.client]
```

*Why this violates the architecture*: Data models are fundamental contracts used throughout the library. Making a model depend on an external adapter tightly couples the entire codebase to that external SDK, breaking provider independence and testability.

---

## Import Philosophy

### Explicit Internal Imports

Internal implementation modules should use explicit, fully-qualified module imports rather than deep relative traversing:

```python
# Preferred internal import
from llm_data_utils.text.normalization import normalize_text
```

### Curated Public API

Package `__init__.py` files should only re-export curated, stable public symbols when deliberately intended for consumers:

```python
# Clean consumer API (when public symbols are formally introduced)
from llm_data_utils.text import normalize_text
```

### Prohibition of Wildcard Imports

Wildcard imports obscure namespace origins and introduce subtle naming conflicts. They are strictly prohibited across the codebase:

```python
# Prohibited
from llm_data_utils.text import *
```
