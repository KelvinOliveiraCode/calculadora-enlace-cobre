"""Permite executar como ``python -m caboclink``.

Enables running as ``python -m caboclink``.
"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())