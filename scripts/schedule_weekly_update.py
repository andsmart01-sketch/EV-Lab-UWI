"""
One-time setup: registers a Windows Task Scheduler task that runs
update_weekly.py every Wednesday at 1:00 PM.

Run once from the terminal:
    python scripts/schedule_weekly_update.py
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT   = Path(__file__).resolve().parent.parent
SCRIPT      = REPO_ROOT / "scripts" / "update_weekly.py"
PYTHON      = sys.executable  # uses whichever Python/env is currently active
TASK_NAME   = "PetrojamWeeklyUpdate"

# XML definition for Task Scheduler
task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-07-29T13:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByWeek>
        <WeeksInterval>1</WeeksInterval>
        <DaysOfWeek>
          <Wednesday/>
        </DaysOfWeek>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>{PYTHON}</Command>
      <Arguments>"{SCRIPT}"</Arguments>
      <WorkingDirectory>{REPO_ROOT}</WorkingDirectory>
    </Exec>
  </Actions>
  <Settings>
    <ExecutionTimeLimit>PT10M</ExecutionTimeLimit>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <StartWhenAvailable>true</StartWhenAvailable>
  </Settings>
</Task>"""

xml_path = REPO_ROOT / "scripts" / "petrojam_task.xml"
xml_path.write_text(task_xml, encoding="utf-16")

result = subprocess.run(
    ["schtasks", "/Create", "/TN", TASK_NAME, "/XML", str(xml_path), "/F"],
    capture_output=True, text=True
)

if result.returncode == 0:
    print(f"Task '{TASK_NAME}' registered successfully.")
    print("It will run every Wednesday at 1:00 PM while your computer is on.")
    print("If the computer is off at 1pm, it will run the next time you turn it on")
    print("(because StartWhenAvailable is enabled).")
else:
    print("ERROR registering task:")
    print(result.stderr)
    print("\nYou may need to run this script as Administrator.")
    print("Right-click VS Code -> Run as administrator, then retry.")
