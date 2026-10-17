# Project Governance

## Constraints First

Before implementation, replace this governance with the actual project's purpose, user outcome, scope, constraints, technology stack, verification and deployment commands. Do not begin application implementation while these are undecided.
No application stack has been selected in this template. Do not report application tests or builds as passed.

## Working Rules

UX first: explain why a technical choice is needed and what changes for users. Search mature open source first; avoid speculative architecture. Define acceptance criteria, make focused changes, then verify actual behavior. Never hide errors to make checks pass.
Use concise English commits with feat / fix / docs / refactor / chore / archive / memory / decision prefixes. Push and deployment require task authorization. Do not store secrets or private context in this public template.

## Directory Contract

- docs/: architecture, development, roadmap and decisions; keep current, retain useful ADR history.
- src/: product code once the stack is selected; no generated builds.
- tests/: behavior tests, not production data or secrets.
- scripts/: necessary repeatable tools and baseline validation.
- assets/: small distributable assets with known provenance; no raw outputs or large media.
- .github/: CI, issue and PR templates.

Folders and ordinary files use lowercase-kebab-case. Exceptions: README.md, CLAUDE.md, AGENTS.md, CHANGELOG.md, LICENSE, ADR-XXXX-title.md, .github/ISSUE_TEMPLATE, .github/PULL_REQUEST_TEMPLATE.md and dotfiles declared here. Empty required folders use .gitkeep. Change governance before adding top-level folders. Review obsolete files and broken links every three months; remove task scratch files when no longer useful.

## Repository Setup

Repository names use lowercase-kebab-case; versions use tags/releases. Every repository has a README, Description and 4–7 relevant Topics. Lifecycle: ACTIVE / MAINTENANCE / EXPERIMENTAL / ARCHIVED. Choose a verified lifecycle at initialization.
This template is MAINTENANCE. Its MIT license covers the template; decide the new project's licensing explicitly and retain required notices for reused template content.

## Data and Validation

PUBLIC may be published. INTERNAL belongs only in private repositories. SECRET never belongs in Git. .env.example uses empty values only. Do not commit passwords, tokens, cookies, private keys, personal documents or raw datasets.
Single-file limit: 10 MiB. Store models/media externally, binaries in Releases; evaluate LFS only when needed.
Run `bash scripts/validate-structure.sh` for baseline structure, local links and secret-pattern checks. This does not test an application. Add stack-specific test/lint/build commands after selecting the stack. If a possible secret is detected, stop commits/push, remove it from working files and index, and report the path/category without printing the value. Historical exposure requires credential revocation and a separately authorized history repair.

## Validation File Scope

校验工作树中已跟踪及未忽略的待纳入文件，并独立校验暂存区。未跟踪且被 .gitignore 忽略的本地依赖、构建目录和 .env 不读取；已跟踪文件不能通过 .gitignore 逃避检查。空的未忽略顶级目录仍按目录规范检查。
