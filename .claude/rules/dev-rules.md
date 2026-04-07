# Dev Rules — NomNom

Standards and conventions for the NomNom project. For workflow and process, see `dev-workflow.md`.

## 1. Quality Gates

Every change must pass these gates before it is considered complete:

### Gate 1: Correctness
- The code does what was requested — no more, no less.
- Edge cases identified during development are handled.
- No regressions introduced to existing functionality.

### Gate 2: Tests
- New features have corresponding tests (or documented reason why not).
- Bug fixes include a regression test that reproduces the original bug.
- All existing tests pass before committing.

### Gate 3: Code Quality
- No linting errors or warnings.
- No `TODO` or `FIXME` left without a linked issue or explanation.
- No dead code, commented-out blocks, or leftover debug statements.
- No unused files, models, services, or imports left in the codebase. If something is replaced, **delete the old version entirely** — don't leave it "for reference."

### Gate 4: Security
- No secrets, credentials, or API keys in the codebase.
- User inputs are validated and sanitized at system boundaries.
- Dependencies are from trusted sources with no known critical vulnerabilities.

### Gate 5: Documentation
- All applicable docs updated per the Iteration Workflow in `dev-workflow.md`.
- Inline comments added only where logic is non-obvious.

## 2. Commit Protocol

### Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary in imperative mood>

<optional body: explain WHAT changed and WHY>

<optional footer: breaking changes, issue refs>
```

### Types

| Type | Use When |
|---|---|
| `feat` | Adding new functionality |
| `fix` | Fixing a bug |
| `docs` | Documentation-only changes |
| `style` | Formatting, whitespace, semicolons (no logic change) |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or updating tests |
| `chore` | Build, tooling, dependency updates |
| `ci` | CI/CD configuration changes |
| `perf` | Performance improvements |

### Rules

- **All tests must pass before committing.** Write tests for new code, run the full suite, fix any failures — only then commit.
- Each commit should be atomic — one logical change per commit.
- Never commit broken code to `main`.
- Never commit generated files, build artifacts, or secrets (including `.DS_Store`, `*.egg-info`, `__pycache__`).
- Always verify with `git diff` before committing.

## 3. Branch Strategy

All work happens directly on `main`. Keep it simple — no feature branches for now.

- Commit directly to `main` after tests pass.
- Each commit should be atomic and leave `main` in a working state.
- If a multi-phase iteration needs isolation in the future, create a branch off `main` and merge back when complete.

## 4. Testing Requirements

### Minimum Coverage

- All public functions must have at least one test.
- Critical paths (auth, LLM orchestration, caching) require comprehensive tests.
- All API endpoints require integration tests.

### Test Structure

```
tests/
  unit/         ← isolated unit tests
  integration/  ← tests involving multiple components or external services
  e2e/          ← end-to-end tests (if applicable)
```

### Naming Convention

- Test files mirror source files: `src/services/ai_service.py` → `tests/unit/services/test_ai_service.py`
- Test names describe behavior: `test_should_return_error_when_food_name_invalid`

### Running Tests

```bash
pytest tests/
```

- Run the full test suite before every commit.
- Fix failing tests before proceeding — never skip or disable tests without explanation and user approval.

## 5. Code Standards

### Naming (Python)

- Variables/functions: `snake_case`.
- Constants: `UPPER_SNAKE_CASE`.
- Classes: `PascalCase`.
- Files/modules: `snake_case`.
- Be descriptive: `get_food_log_by_id` over `get_log`, `is_authenticated` over `check`.

### Naming (Swift/iOS)

- Variables/properties: `camelCase`.
- Functions/methods: `camelCase`.
- Classes/structs: `PascalCase`.
- Constants: `camelCase` in code, but use `UPPER_SNAKE_CASE` for config values.

### Error Handling

- Never silently swallow errors.
- Use structured error types and HTTP status codes.
- Log errors with sufficient context for debugging.
- Return meaningful error responses to the iOS client.

### General Principles

- **Readability over cleverness.** Code is read far more often than it is written.
- **Single Responsibility.** Each function/module does one thing well.
- **DRY, but not prematurely.** Three similar lines are better than a premature abstraction.
- **Explicit over implicit.** Favor clarity even if it's slightly more verbose.
- **Fail fast.** Validate inputs early, return early, avoid deep nesting.

### Cleanup & No Backward Compatibility

- **When replacing a system, delete the old one completely.** Remove the old model, service, tests, imports, and documentation references. No shims, no "keep for now," no re-exports. Leaving old code around creates confusion.
- **Delete aggressively.** If a file, function, model, or test is no longer used, delete it in the same commit that introduces the replacement. Don't defer cleanup to a separate task — it won't happen.
- **Grep before you're done.** After replacing a system, search the entire codebase for references to the old names. Remove every one. Zero references to the old system should remain.

### Dependencies

- Prefer well-maintained, widely-used libraries.
- Pin dependency versions for reproducibility.
- Audit new dependencies before adding them.
- Remove unused dependencies promptly.

## 6. AI-Specific Rules

These rules apply specifically when AI (Claude) is performing development work:

1. **Always read before writing.** Never modify a file without reading it first.
2. **Show your reasoning.** For non-trivial decisions, explain why you chose an approach.
3. **Ask, don't assume.** If requirements are ambiguous, ask the user.
4. **Stay in scope.** Only make changes that are directly requested or clearly necessary.
5. **Verify your work.** Run tests, check output, read the result — don't assume success.
6. **Update project docs.** Follow the Iteration Workflow in `dev-workflow.md` so the next session can pick up seamlessly.
7. **Respect user decisions.** If the user overrides a suggestion, follow their direction.
8. **No hallucinated imports.** Only use libraries/modules that are actually installed in the project.
9. **Keep CLAUDE.md clean.** CLAUDE.md should reference detailed docs, not duplicate their content.
