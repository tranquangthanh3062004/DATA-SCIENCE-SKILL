"""Cross-platform cleanup of build artifacts and caches (replaces find/rm in Makefile)."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".venv", ".git", "node_modules"}
CACHE_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
TOP_LEVEL = ["dist", "build", "htmlcov", "reports"]


def _walk(base: Path) -> list[Path]:
    found: list[Path] = []
    for path in base.iterdir():
        if path.name in SKIP_DIRS:
            continue
        if path.is_dir():
            if path.name in CACHE_NAMES:
                found.append(path)
            else:
                found.extend(_walk(path))
    return found


def main() -> None:
    targets = _walk(ROOT)
    targets += [ROOT / name for name in TOP_LEVEL if (ROOT / name).exists()]
    targets += list(ROOT.glob("*.egg-info"))
    for target in targets:
        shutil.rmtree(target, ignore_errors=True)
    print(f"Cleaned {len(targets)} artifact paths")


if __name__ == "__main__":
    main()
