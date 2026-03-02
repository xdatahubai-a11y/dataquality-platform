## Task
Refactor: {{title}}

## Motivation
{{motivation}}

## Scope
Files to refactor:
{{target_files}}

## Approach
{{approach}}

## Constraints
- Zero behavior change — all existing tests must pass without modification
- If a test needs updating, the refactor is changing behavior (stop and flag it)
- Keep commits atomic and well-described

## Git Operations (YOU must do all of these)
1. Complete the refactoring
2. Run all tests — they must pass WITHOUT modification
3. Run lint/type checks and fix any errors
4. Commit all changes: `git add -A && git commit -m "refactor: {{title}}"`
5. Push to remote: `git push origin {{branch}}`
6. Create the PR: `gh pr create --title "refactor: {{title}}" --body "Closes #{{issue_number}}" --base main --head {{branch}} --repo {{repo}}`

Do NOT stop until the PR is created. If any step fails, fix it and retry.

## Definition of Done
- [ ] Refactoring complete
- [ ] All existing tests pass WITHOUT modification
- [ ] No lint or type errors
- [ ] Changes committed, pushed, and PR created
