# Contributing

This document defines the branch, commit, and pull request conventions used in this project.

## Branch Naming

Use the following pattern:

```text
type/short-description
```

### Types

- `feat`: new functionality
- `fix`: bug fix
- `refactor`: code restructuring without changing behavior
- `test`: tests
- `docs`: documentation
- `chore`: repository or configuration changes

### Rules

- Use lowercase letters.
- Separate words with hyphens.
- Keep branch names short and descriptive.
- Create branches from `main`.
- Use the same type names used by the commit convention.

### Examples

```text
feat/maze-parser
feat/bfs
feat/door-validation
fix/locked-door-validation
refactor/search-state
test/bfs-edge-cases
docs/update-readme
chore/add-gitkeep
```

## Commit Convention

Use the following format:

```text
type: short description

[Description]
Optional additional context.

[Rationale]
Optional explanation of why the change was made.

[Solution]
Optional explanation of how a non-trivial problem was solved.
```

The commit title should be concise and written in the imperative mood.

### Types

- `feat`: new functionality
- `fix`: bug fix
- `refactor`: code restructuring without changing behavior
- `test`: tests
- `docs`: documentation
- `chore`: repository or configuration changes

### Examples

```text
feat: implement BFS search

[Description]
Add breadth-first search for navigating the maze.
```

```text
fix: include collected keys in visited states

[Description]
Different key sets must represent different search states.

[Solution]
Use the current position and collected keys as the state identifier.
```

For simple changes, the body may be omitted:

```text
docs: update project setup instructions
```

## Pull Requests

- Create a branch from `main`.
- Keep changes focused on a single purpose whenever possible.
- Make focused commits.
- Push the branch.
- Open a pull request into `main`.
- Have at least one teammate review it before merging.
- Resolve review comments before merging.

## Workflow Example

```text
Branch:
feat/bfs-search

Commits:
feat: add BFS queue handling
feat: track visited states
test: add BFS search scenarios

Pull Request:
Implement BFS search
```
