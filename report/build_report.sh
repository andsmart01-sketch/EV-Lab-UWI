#!/usr/bin/env bash
# Rebuild full_report.md from the numbered sections, then the Word document.
#
# The MARKDOWN SECTIONS are the source of truth. full_report.md and the .docx
# are both generated, so edits made directly to either are lost the next time
# this runs. Edit section_0N_*.md.
set -e
cd "$(dirname "$0")"
python3 - <<'PY'
from pathlib import Path
secs = sorted(Path('.').glob('section_0*.md'))
parts = [s.read_text(encoding='utf-8').rstrip() for s in secs]
Path('full_report.md').write_text("\n\n---\n\n".join(parts) + "\n", encoding='utf-8')
print(f"full_report.md rebuilt from {len(secs)} sections, "
      f"{sum(len(p.split()) for p in parts):,} words")
PY
pandoc full_report.md -o EV_Lab_Report_2026.docx --toc --toc-depth=2
echo "EV_Lab_Report_2026.docx rebuilt"
