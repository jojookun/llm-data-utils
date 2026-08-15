# Development Workflow

This document outlines the branching strategy, commit conventions, and Pull Request workflow for `llm-data-utils`.

---

## Development Lifecycle

All contributions follow a lightweight GitHub Flow model:

```text
main
  ↓
short-lived branch
  ↓
implement
  ↓
validate
  ↓
commit
  ↓
push
  ↓
Pull Request
  ↓
review
  ↓
merge
```

---

## Main Branch

* `main` is the primary, stable integration branch.
* Production-ready and verified code resides on `main`.
* Direct commits to `main` should be avoided; all changes must arrive via reviewed Pull Requests.

---

## Branch Naming

All development occurs on short-lived feature, fix, or maintenance branches. Use descriptive, kebab-case names prefixed by the change category:

| Prefix | Purpose | Example |
| :--- | :--- | :--- |
| `feat/` | Introducing new functionality | `feat/text-normalizer` |
| `fix/` | Bug fixes and patches | `fix/empty-input-handling` |
| `docs/` | Documentation additions or updates | `docs/gemini-setup` |
| `refactor/` | Code refactoring without changing public behavior | `refactor/string-pipeline` |
| `test/` | Adding or updating tests | `test/text-normalizer` |
| `chore/` | Maintenance, tooling, and build configuration | `chore/update-tooling` |

---

## Conventional Commits

Commits must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
<type>[optional scope]: <description>
```

### Commit Types

* **`feat`**: A new feature for the user or consumer.
* **`fix`**: A bug fix.
* **`docs`**: Documentation changes only.
* **`refactor`**: Code change that neither fixes a bug nor adds a feature.
* **`test`**: Adding missing tests or correcting existing tests.
* **`chore`**: Changes to the build process, tooling, or auxiliary files.

### Examples

* `feat(text): add whitespace normalization`
* `fix(parser): handle empty input safely`
* `docs: document development workflow`
* `refactor(core): simplify processing pipeline`
* `test(text): add normalization edge cases`
* `chore: update development tooling`

### Breaking Changes

When introducing breaking changes, append `!` after the type/scope (e.g. `feat(api)!: change default normalization mode`) or include a `BREAKING CHANGE:` footer in the commit message body.

---

## Pull Request Workflow

To submit a change to the repository, follow these 12 steps:

1. **Update local `main`**: Ensure your local `main` is synchronized with `origin/main` (`git switch main && git pull --ff-only origin main`).
2. **Create a branch**: Create a focused branch (`git switch -c feat/my-feature`).
3. **Implement one focused change**: Keep modifications scoped to the single task at hand.
4. **Validate locally**: Run local test suites, linters, and verification checks in the virtual environment.
5. **Review diff**: Inspect staged changes with `git diff` to ensure no unintended files or secrets are included.
6. **Create a Conventional Commit**: Commit with a clear, standard message (`git commit -m "feat(module): description"`).
7. **Push the branch**: Push your branch to GitHub (`git push -u origin feat/my-feature`).
8. **Open a Pull Request**: Open a PR targeting `main` on GitHub using the repository Pull Request template.
9. **Review**: Participate in code review, addressing feedback if needed.
10. **Merge**: Once approved and checks pass, merge the PR into `main`.
11. **Delete the merged branch**: Delete the remote and local feature branches to keep the repository tidy.
12. **Synchronize local `main`**: Switch back to `main` and pull the latest changes (`git switch main && git pull --ff-only origin main`).
