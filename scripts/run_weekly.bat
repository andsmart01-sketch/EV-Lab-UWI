@echo off
REM ====================================================================
REM  run_weekly.bat - automatic weekly price update for the EV dashboard
REM
REM  This is what Windows Task Scheduler runs. It activates the conda
REM  environment, runs the updater, and appends everything it printed to
REM  a log so a silent failure at 6pm on a Thursday is still visible on
REM  Friday morning.
REM
REM  To install the schedule, run install_schedule.bat ONCE, as your
REM  normal user. You do not need administrator rights.
REM ====================================================================

set REPO=%~dp0..
set LOGDIR=%REPO%\logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

REM Contact address sent in the User-Agent. Set this to a departmental or
REM project address, not a personal one. It ends up in Petrojam's server
REM logs and should outlive whoever is running the code.
if "%EVLAB_CONTACT%"=="" set EVLAB_CONTACT=evlab@uwimona.edu.jm

call conda activate EVlab 2>nul
if errorlevel 1 (
    echo [%date% %time%] Could not activate conda env EVlab >> "%LOGDIR%\weekly.log"
)

echo. >> "%LOGDIR%\weekly.log"
echo ================================================== >> "%LOGDIR%\weekly.log"
echo [%date% %time%] starting >> "%LOGDIR%\weekly.log"

python "%REPO%\scripts\update_weekly.py" %* >> "%LOGDIR%\weekly.log" 2>&1

echo [%date% %time%] exit code %errorlevel% >> "%LOGDIR%\weekly.log"
