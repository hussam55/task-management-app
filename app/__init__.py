"""Task Management API package bootstrap."""

from __future__ import annotations

import os
from pathlib import Path


def _load_dotenv() -> None:
	"""Load key/value pairs from .env into process env if not already set."""
	env_path = Path(__file__).resolve().parent.parent / ".env"
	if not env_path.exists():
		return

	for raw_line in env_path.read_text(encoding="utf-8").splitlines():
		line = raw_line.strip()
		if not line or line.startswith("#") or "=" not in line:
			continue

		key, value = line.split("=", 1)
		key = key.strip()
		value = value.strip().strip('"').strip("'")
		if key and key not in os.environ:
			os.environ[key] = value


_load_dotenv()
