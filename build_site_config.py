from __future__ import annotations

import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
config = tomllib.loads((ROOT / "site-config.toml").read_text(encoding="utf-8"))

(ROOT / "site-config.js").write_text(
    "window.SITE_CONFIG = "
    + json.dumps(config, ensure_ascii=False, indent=2)
    + ";\n",
    encoding="utf-8",
)

print("Updated site-config.js from site-config.toml")
