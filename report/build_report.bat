@echo off
REM Rebuild the report. Run from anywhere; edits belong in the section_0N_*.md
REM files, since full_report.md and the .docx are both generated.
cd /d "%~dp0"
python -c "from pathlib import Path; secs=sorted(Path('.').glob('section_0*.md')); parts=[s.read_text(encoding='utf-8').rstrip() for s in secs]; Path('full_report.md').write_text(chr(10).join(['']*0) + ('%s' %% ('\n\n---\n\n'.join(parts))) + chr(10), encoding='utf-8'); print('full_report.md rebuilt from %%d sections' %% len(secs))"
pandoc full_report.md -o EV_Lab_Report_2026.docx --toc --toc-depth=2
echo Done. EV_Lab_Report_2026.docx rebuilt.
pause
