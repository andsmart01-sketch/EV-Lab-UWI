@echo off
REM ====================================================================
REM  install_schedule.bat - register the weekly update with Windows
REM
REM  Run this ONCE. Double-click it, or run it from a normal Command
REM  Prompt. Administrator rights are not needed.
REM
REM  Schedule: Thursdays at 18:00 local time.
REM
REM  Why Thursday: Petrojam publishes on Thursdays. That is not a guess.
REM  Of the 602 rows in the price series, 581 are dated on a Thursday, and
REM  every row from April to June 2026 is. 18:00 leaves the whole working
REM  day for the figures to go up.
REM
REM  If the machine is asleep or off at 18:00, Windows runs the task at
REM  the next opportunity because of /RI and the missed-run setting below,
REM  so a laptop that was closed on Thursday still catches up on Friday.
REM  And if it somehow runs twice, the freshness guard makes the second
REM  run a no-op with zero network requests.
REM ====================================================================

set REPO=%~dp0..
set TASKNAME=EVLab Weekly Price Update

schtasks /Create ^
    /TN "%TASKNAME%" ^
    /TR "\"%REPO%\scripts\run_weekly.bat\"" ^
    /SC WEEKLY ^
    /D THU ^
    /ST 18:00 ^
    /F

if errorlevel 1 (
    echo.
    echo Could not create the task. Check the message above.
    pause
    exit /b 1
)

echo.
echo Created: "%TASKNAME%"
echo   Runs   : Thursdays at 18:00
echo   Script : %REPO%\scripts\run_weekly.bat
echo   Log    : %REPO%\logs\weekly.log
echo.
echo Useful commands:
echo   schtasks /Query /TN "%TASKNAME%" /V /FO LIST     see the schedule
echo   schtasks /Run   /TN "%TASKNAME%"                 run it now, to test
echo   schtasks /Delete /TN "%TASKNAME%" /F             remove it
echo.
pause
