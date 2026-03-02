## Task
Fix bug: {{title}}

## Error Details
{{error_details}}

## Steps to Reproduce
{{reproduction_steps}}

## Technical Guidance
- Start by reading the error trace and understanding the root cause
- Key files likely involved:
{{key_files}}
- Related test files:
{{test_files}}

## Constraints
- Fix the root cause, not just the symptom
- Do NOT refactor surrounding code
- Add a regression test for this specific bug

## Git Operations (YOU must do all of these)
1. Fix the bug and add regression test
2. Run all tests and fix any failures
3. Run lint/type checks and fix any errors
4. Commit all changes: `git add -A && git commit -m "fix: {{title}}"`
5. Push to remote: `git push origin {{branch}}`
6. Create the PR: `gh pr create --title "fix: {{title}}" --body "Closes #{{issue_number}}" --base main --head {{branch}} --repo {{repo}}`

Do NOT stop until the PR is created. If any step fails, fix it and retry.

## Definition of Done
- [ ] Bug fixed at root cause
- [ ] Regression test added
- [ ] All existing tests still pass
- [ ] No lint or type errors
- [ ] Changes committed, pushed, and PR created
