# Project Repository Template

A minimal, governance-first starting point for product repositories.

Lifecycle: MAINTENANCE (template only).

## Start Here

1. Use this template to create an explicitly authorized project repository.
2. Replace this README with the product purpose, audience and verified status.
3. Complete [CLAUDE.md](CLAUDE.md) first: scope, stack, directory rules, validation and deployment.
4. Choose project licensing and visibility; update description and 4–7 relevant Topics.
5. Implement only after constraints and acceptance criteria are clear.

## Documentation

[Architecture](docs/architecture.md) · [Development](docs/development.md) · [Roadmap](docs/roadmap.md)

Product code goes in src/, behavior checks in tests/, small assets in assets/, repeatable tooling in scripts/ and ADRs in docs/decisions/.

## Verification

Requires Bash, Python 3 and Git. Run `bash scripts/validate-structure.sh`.
This checks baseline structure, local Markdown links, filenames, file sizes and selected secret patterns. It does not verify external URLs or prove that all secrets are absent.
No application stack, application tests, build or deployment has been configured. Define those commands in docs/development.md before application work.

## License

[MIT](LICENSE) applies to this template. Choose licensing explicitly for the new product and retain attribution required for template content you reuse.
