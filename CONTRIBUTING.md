# Contributing to ADI-OS

## Workflow
1. Fork and create a branch: `git checkout -b feat/<short-name>`.
2. Install: `uv sync --extra dev` then `uv run pre-commit install`.
3. Make changes with tests. Follow [Conventional Commits](https://www.conventionalcommits.org/).
4. Run all local gates before opening a PR:
   ```bash
   make lint
   make typecheck
   make test
   ```
5. Open a PR using the template in `.github/pull_request_template.md`.

## Standards
- Python 3.11+, fully typed (`mypy --strict` must pass on `src/`).
- No hardcoded secrets; use `.env` (see `.env.example`).
- New pipelines extend `BasePipeline` and must be idempotent.
- New metrics must be registered in `configs/metric_registry.yml`.
- Every claim in reports carries an evidence tag (see `.agents/rules/data-org-rules.md`).
- Never fabricate data. Synthetic data must be labeled `SYNTHETIC`.

## Reviews
Model and data-contract changes require an independent reviewer (Gate 6). No self-approval.
