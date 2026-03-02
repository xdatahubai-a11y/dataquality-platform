## Task
Implement: {{title}}

## Context
{{context}}

## Requirements
{{requirements}}

## Technical Guidance
- This is a {{language}} project using {{framework}}
- Follow existing patterns in the codebase
- Key files to reference:
{{key_files}}

## Constraints
- Do NOT modify: {{exclude_patterns}}
- Keep changes focused — do not refactor unrelated code
- Follow existing code style and naming conventions

## Git Operations (YOU must do all of these)
1. Implement the feature
2. Run tests and fix any failures
3. Run lint/type checks and fix any errors
4. Commit all changes: `git add -A && git commit -m "feat: {{title}}"`
5. Push to remote: `git push origin {{branch}}`
6. Create the PR: `gh pr create --title "feat: {{title}}" --body "Closes #{{issue_number}}" --base main --head {{branch}} --repo {{repo}}`

Do NOT stop until the PR is created. If any step fails, fix it and retry.

## Definition of Done
- [ ] Feature implemented as described
- [ ] Unit tests cover new functionality
- [ ] All existing tests still pass
- [ ] No lint or type errors
- [ ] Changes committed, pushed, and PR created
