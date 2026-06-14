from __future__ import annotations

import secrets
import string


def new_id(prefix: str) -> str:
    alphabet = string.ascii_lowercase + string.digits
    suffix = "".join(secrets.choice(alphabet) for _ in range(12))
    return f"{prefix}_{suffix}"
