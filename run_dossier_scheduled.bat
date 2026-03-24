@echo off
REM Dossier Scheduled Task Runner - Bulletproof version
REM Captures all output to a timestamped log file

SET PYTHON="C:\Users\Carzl\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\python.exe"
SET WORKDIR="C:\Users\Carzl\Documents\Projects\GITHUB\daily-dossier"
SET LOGDIR="C:\Users\Carzl\Documents\Projects\Python Stuff\Reddit Helper Helper\OUTPUT"

REM Create log filename with timestamp
FOR /F "tokens=2-4 delims=/ " %%a IN ('date /t') DO SET DATESTR=%%c%%a%%b
FOR /F "tokens=1-2 delims=: " %%a IN ('time /t') DO SET TIMESTR=%%a%%b
SET LOGFILE=%LOGDIR%\task_%DATESTR%_%TIMESTR%.log

echo [%DATE% %TIME%] Starting dossier update >> %LOGDIR%\task_history.log

cd /d %WORKDIR%
%PYTHON% run_full_digest.py >> %LOGFILE% 2>&1

IF %ERRORLEVEL% EQU 0 (
    echo [%DATE% %TIME%] SUCCESS >> %LOGDIR%\task_history.log
) ELSE (
    echo [%DATE% %TIME%] FAILED with exit code %ERRORLEVEL% >> %LOGDIR%\task_history.log
    echo [%DATE% %TIME%] See log: %LOGFILE% >> %LOGDIR%\task_history.log
)
