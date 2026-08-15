# Developer Environment Setup

This guide details how to configure a reproducible local Python environment for contributing to `llm-data-utils`.

---

## Requirements

Ensure you have the following prerequisites installed:

* **Python**: Version `>= 3.11` (CPython, MSYS2/UCRT64, or any standard Python 3.11+ distribution)
* **pip**: Standard Python package installer
* **Git**: Version control system
* **GitHub CLI (`gh`)** *(optional)*: Recommended for managing Pull Requests and repository workflows

---

## Creating a Virtual Environment

Always use an isolated virtual environment (`.venv`) for local development.

### Windows (Standard CPython)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> **Note**: If your Windows environment uses MSYS2 or UCRT64 Python, the environment adopts a POSIX directory layout where the binary is located at `.venv/bin/python.exe`.

### macOS & Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Installing the Project

### Standard Editable Installation

To install the core library in editable mode for general use:

```bash
python -m pip install -e .
```

### Development Installation

To install the library along with developer tooling (`pytest`, `ruff`, `mypy`):

```bash
python -m pip install -e ".[dev]"
```

The `dev` extra includes linting, formatting, type checking, and test framework tools necessary for contributors. Normal library consumers do not need these dependencies.

---

## Environment Variables

The repository provides a template for local environment variables:

* **[`.env.example`](../.env.example)**: Tracked in version control, contains variable keys without sensitive values.
* **`.env`**: Local file ignored by Git, used for storing actual local configuration and keys. **Never commit `.env` or credentials.**

### Local Setup

Copy the template to create your local `.env`:

```bash
# Windows PowerShell
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

### Supported Variables

* **`GEMINI_API_KEY`**: Reserved for future Gemini integration. Currently unused by application code and not required for Day 3 development.

---

## Dependency Policy

1. **Runtime Dependencies**: Added under `dependencies` in `pyproject.toml` only when essential for the library's core features.
2. **Development Tooling**: Added under `[project.optional-dependencies]` in the `dev` group.
3. **Zero Secrets in Packaging**: Secrets or environment tokens must never be placed in `pyproject.toml` or source code.
4. **Minimal Footprint**: Keep external dependencies minimal, favoring standard library implementations whenever practical.
