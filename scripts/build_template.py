"""Embed tested src/handler.py into CloudFormation template.yaml (no packages needed)."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root / "src" / "handler.py").read_text(encoding="utf-8")
input_template = (root / "infra" / "template.base.yaml").read_text(encoding="utf-8")
marker = "          __PYTHON_CODE__\n"
if input_template.count(marker) != 1:
    raise SystemExit("Expected exactly one inline-code marker")
indented = "".join("          " + line if line.strip() else "\n" for line in source.splitlines(keepends=True))
out = input_template.replace(marker, indented)
(root / "template.yaml").write_text(out, encoding="utf-8")
print("Built template.yaml from src/handler.py")
