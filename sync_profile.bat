@echo off
title Shallot Profile Synchronizer
echo ========================================================
echo        Shallot (strothman) Profile Auto-Sync Engine
echo ========================================================
echo.

cd /d "%~dp0"
python sync_profile.py --push

echo.
echo ========================================================
echo        Sync Complete! Press any key to exit...
echo ========================================================
pause >nul
